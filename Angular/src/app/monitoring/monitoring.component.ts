// Componente para el panel de monitoreo de la API (solo administradores)
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';

const backendApi = `http://127.0.0.1:8000/api/v1`;

// Estructura de una entrada de bitácora
interface LogEntry {
  tipo: string;
  cuerpo: string;
  fechahora: string;
}

// Estructura de las métricas de monitoreo
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
    private http: HttpClient,
    private router: Router,
    private authService: AuthService
  ) { }

  // Al iniciar, carga las métricas y la bitácora
  ngOnInit(): void {
    this.loadMetrics();
    this.loadLogs();
  }

  // Obtiene los headers con el token de autenticación
  getAuthHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Token ${token}`
    });
  }

  // Carga las métricas de monitoreo desde el servidor
  loadMetrics(): void {
    this.isLoading.set(true);
    this.error.set(null);

    const token = this.authService.getToken();
    if (!token) {
      this.isLoading.set(false);
      this.error.set('Por favor, inicia sesión.');
      this.router.navigate(['/login']);
      return;
    }

    const headers = this.getAuthHeaders();
    const hours = this.selectedHours();

    // Solicita las métricas al servidor
    this.http.get<MonitoringMetrics>(
      `${backendApi}/logger/monitoring/dashboard?hours=${hours}`,
      { headers }
    ).subscribe({
      next: (data) => {
        this.metrics.set(data);
        this.isLoading.set(false);
      },
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

  // Cambia el rango de tiempo y recarga las métricas
  onTimeRangeChange(hours: number): void {
    this.selectedHours.set(hours);
    this.loadMetrics();
  }

  // Obtiene el color según el código de estado HTTP
  getStatusColor(statusCode: number): string {
    if (statusCode >= 500) return 'text-red-500';
    if (statusCode >= 400) return 'text-orange-500';
    if (statusCode >= 300) return 'text-yellow-500';
    return 'text-green-500';
  }

  // Obtiene el color del badge según el código de estado
  getStatusBadgeColor(statusCode: number): string {
    if (statusCode >= 500) return 'bg-red-500/20 text-red-300 border-red-500';
    if (statusCode >= 400) return 'bg-orange-500/20 text-orange-300 border-orange-500';
    if (statusCode >= 300) return 'bg-yellow-500/20 text-yellow-300 border-yellow-500';
    return 'bg-green-500/20 text-green-300 border-green-500';
  }

  // Formatea un número con separadores de miles
  formatNumber(num: number): string {
    return num.toLocaleString('es-ES');
  }

  // Formatea el tiempo en milisegundos o segundos
  formatTime(ms: number): string {
    if (ms < 1000) return `${ms.toFixed(2)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  }

  // Carga las últimas 100 entradas de la bitácora
  loadLogs(): void {
    this.isLoadingLogs.set(true);

    const token = this.authService.getToken();
    if (!token) {
      this.isLoadingLogs.set(false);
      return;
    }

    const headers = this.getAuthHeaders();

    // Solicita las entradas de la bitácora al servidor
    this.http.get<LogEntry[]>(
      `${backendApi}/logger/monitoring/logs`,
      { headers }
    ).subscribe({
      next: (data) => {
        this.logs.set(data);
        this.isLoadingLogs.set(false);
      },
      error: (err) => {
        this.isLoadingLogs.set(false);
        console.error('Error al cargar la bitácora:', err);
      }
    });
  }

  // Obtiene el color según el tipo de log
  getLogTypeColor(tipo: string): string {
    switch (tipo) {
      case 'ERROR':
        return 'text-red-400';
      case 'CRUD':
        return 'text-blue-400';
      case 'ACTION':
        return 'text-yellow-400';
      case 'RESPONSETIME':
        return 'text-green-400';
      default:
        return 'text-gray-400';
    }
  }

  // Obtiene el color del badge según el tipo de log
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

