//componente para el panel de monitoreo de la API (solo administradores)
//muestra métricas, errores y logs del sistema
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';

//URL base del backend
const backendApi = `http://127.0.0.1:8000/api/v1`;

//interfaz: estructura de una entrada de bitácora (log del sistema)
interface LogEntry {
  tipo: string; //tipo de log (CRUD, ERROR, ACTION, RESPONSETIME)
  cuerpo: string; //mensaje del log
  fechahora: string; //fecha y hora del log
}

//interfaz: estructura completa de las métricas de monitoreo que vienen del backend
interface MonitoringMetrics {
  time_range_hours: number;
  total_requests: number;
  average_response_time_ms: number;
  error_count: number;
  error_rate_percent: number;
  error_breakdown: Array<{ status_code: number; count: number }>;
  status_distribution: Array<{ status_code: number; count: number }>;
  top_endpoints: Array<{
    endpoint: string;
    method: string;
    count: number;
    avg_response_time: number;
    error_count: number;
  }>;
  recent_errors: Array<{
    request_id: string;
    timestamp: string;
    timestamp_formatted: string;
    method: string;
    endpoint: string;
    status_code: number;
    response_time_ms: number;
    user_username: string | null;
    ip_address: string | null;
    error_message: string | null;
    stack_trace: string | null;
  }>;
}

@Component({
  selector: 'app-monitoring',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './monitoring.component.html',
  styleUrl: './monitoring.component.css'
})
export class MonitoringComponent implements OnInit {
  metrics = signal<MonitoringMetrics | null>(null); // Métricas de monitoreo
  logs = signal<LogEntry[]>([]); // Entradas de la bitácora
  isLoading = signal(false); // Indica si está cargando
  isLoadingLogs = signal(false); // Indica si está cargando la bitácora
  error = signal<string | null>(null); // Mensaje de error
  selectedHours = signal(24); // Horas seleccionadas para el rango
  timeRanges = [1, 6, 12, 24, 48, 72]; // Opciones de rango de tiempo

  constructor(
    private http: HttpClient, //servicio HTTP para hacer peticiones
    private router: Router, //servicio de navegación
    private authService: AuthService //servicio de autenticación
  ) { }

  //se ejecuta cuando el componente se inicializa
  //carga las métricas y la bitácora automáticamente
  ngOnInit(): void {
    this.loadMetrics();
    this.loadLogs();
  }

  //obtiene los headers HTTP con el token de autenticación
  //necesario para las peticiones al backend (solo admin)
  getAuthHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Token ${token}` //formato: "Token <token_value>"
    });
  }

  //carga las métricas de monitoreo desde el servidor
  //hace una petición GET al endpoint del dashboard de monitoreo
  loadMetrics(): void {
    this.isLoading.set(true);
    this.error.set(null);

    //verifica que haya un token de autenticación
    const token = this.authService.getToken();
    if (!token) {
      this.isLoading.set(false);
      this.error.set('Por favor, inicia sesión.');
      this.router.navigate(['/login']);
      return;
    }

    const headers = this.getAuthHeaders();
    const hours = this.selectedHours();

    //solicita las métricas al servidor con el rango de tiempo seleccionado
    this.http.get<MonitoringMetrics>(
      `${backendApi}/logger/monitoring/dashboard?hours=${hours}`,
      { headers }
    ).subscribe({
      //si la petición es exitosa
      next: (data) => {
        this.metrics.set(data);
        this.isLoading.set(false);
      },
      //si hay un error en la petición
      error: (err) => {
        this.isLoading.set(false);
        console.error('Monitoring dashboard error:', err);
        console.error('Error details:', {
          status: err.status,
          statusText: err.statusText,
          error: err.error,
          message: err.message,
          url: err.url
        });

        //procesa diferentes tipos de errores HTTP
        if (err.status === 403) {
          this.error.set('Acceso denegado. Se requieren privilegios de administrador.');
        } else if (err.status === 401) {
          this.error.set('Autenticación requerida. Por favor, inicia sesión nuevamente.');
          this.authService.logout();
        } else if (err.status === 0) {
          this.error.set('No se puede conectar al servidor.');
        } else if (err.status === 404) {
          this.error.set('Endpoint de monitoreo no encontrado.');
        } else if (err.status === 500) {
          const detail = err.error?.detail || err.error?.error || 'Error interno del servidor';
          this.error.set(`Error del servidor: ${detail}.`);
        } else if (err.error && err.error.detail) {
          this.error.set(`Error: ${err.error.detail}`);
        } else if (err.error && typeof err.error === 'string') {
          this.error.set(`Error: ${err.error}`);
        } else if (err.error && err.error.error) {
          this.error.set(`Error: ${err.error.error}`);
        } else {
          const errorMsg = err.message || `HTTP ${err.status || 'Desconocido'}`;
          this.error.set(`Error al cargar datos de monitoreo: ${errorMsg}. Por favor, revisa la consola para más detalles.`);
        }
      }
    });
  }

  //cambia el rango de tiempo seleccionado y recarga las métricas
  //se ejecuta cuando el usuario selecciona un nuevo rango de tiempo
  onTimeRangeChange(hours: number): void {
    this.selectedHours.set(hours);
    this.loadMetrics(); //recarga las métricas con el nuevo rango
  }

  //obtiene el color del texto según el código de estado HTTP
  //se usa en el template para colorear los códigos de estado
  getStatusColor(statusCode: number): string {
    if (statusCode >= 500) return 'text-red-500'; //errores del servidor (500-599)
    if (statusCode >= 400) return 'text-orange-500'; //errores del cliente (400-499)
    if (statusCode >= 300) return 'text-yellow-500'; //redirecciones (300-399)
    return 'text-green-500'; //éxito (200-299)
  }

  //obtiene el color del badge (etiqueta) según el código de estado HTTP
  //se usa en el template para mostrar badges con colores
  getStatusBadgeColor(statusCode: number): string {
    if (statusCode >= 500) return 'bg-red-500/20 text-red-300 border-red-500';
    if (statusCode >= 400) return 'bg-orange-500/20 text-orange-300 border-orange-500';
    if (statusCode >= 300) return 'bg-yellow-500/20 text-yellow-300 border-yellow-500';
    return 'bg-green-500/20 text-green-300 border-green-500';
  }

  //formatea un número agregando separadores de miles (formato español)
  //ejemplo: 1000000 -> "1.000.000"
  formatNumber(num: number): string {
    return num.toLocaleString('es-ES');
  }

  //formatea el tiempo mostrando milisegundos o segundos según corresponda
  //ejemplo: 500 -> "500.00ms", 1500 -> "1.50s"
  formatTime(ms: number): string {
    if (ms < 1000) return `${ms.toFixed(2)}ms`; //menos de 1 segundo: muestra ms
    return `${(ms / 1000).toFixed(2)}s`; //1 segundo o más: muestra segundos
  }

  //carga las últimas 100 entradas de la bitácora desde el servidor
  //hace una petición GET al endpoint de logs
  loadLogs(): void {
    this.isLoadingLogs.set(true);

    //verifica que haya un token de autenticación
    const token = this.authService.getToken();
    if (!token) {
      this.isLoadingLogs.set(false);
      return;
    }

    const headers = this.getAuthHeaders();

    //solicita las entradas de la bitácora al servidor
    this.http.get<LogEntry[]>(
      `${backendApi}/logger/monitoring/logs`,
      { headers }
    ).subscribe({
      //si la petición es exitosa
      next: (data) => {
        this.logs.set(data);
        this.isLoadingLogs.set(false);
      },
      //si hay un error
      error: (err) => {
        this.isLoadingLogs.set(false);
        console.error('Error al cargar la bitácora:', err);
      }
    });
  }

  //obtiene el color del texto según el tipo de log
  //se usa en el template para colorear los tipos de log
  getLogTypeColor(tipo: string): string {
    switch (tipo) {
      case 'ERROR':
        return 'text-red-400'; //errores en rojo
      case 'CRUD':
        return 'text-blue-400'; //operaciones CRUD en azul
      case 'ACTION':
        return 'text-yellow-400'; //acciones en amarillo
      case 'RESPONSETIME':
        return 'text-green-400'; //tiempos de respuesta en verde
      default:
        return 'text-gray-400'; //otros tipos en gris
    }
  }

  //obtiene el color del badge según el tipo de log
  //se usa en el template para mostrar badges con colores
  getLogTypeBadgeColor(tipo: string): string {
    switch (tipo) {
      case 'ERROR':
        return 'bg-red-500/20 text-red-300 border-red-500';
      case 'CRUD':
        return 'bg-blue-500/20 text-blue-300 border-blue-500';
      case 'ACTION':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500';
      case 'RESPONSETIME':
        return 'bg-green-500/20 text-green-300 border-green-500';
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500';
    }
  }
}

