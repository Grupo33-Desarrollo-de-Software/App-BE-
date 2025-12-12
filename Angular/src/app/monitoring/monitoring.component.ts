import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';

const backendApi = `http://127.0.0.1:8000/api/v1`;

interface MonitoringMetrics {
  time_range_hours: number;
  total_requests: number;
  average_response_time_ms: number;
  error_count: number;
  error_rate_percent: number;
  error_breakdown: Array<{ status_code: number; count: number }>;
  status_distribution: Array<{ status_code: number; count: number }>;
  response_time_stats: {
    min: number;
    max: number;
    avg: number;
  };
  requests_per_hour: Array<{
    hour: string;
    count: number;
    avg_response_time: number;
  }>;
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
  metrics = signal<MonitoringMetrics | null>(null);
  isLoading = signal(false);
  error = signal<string | null>(null);
  selectedHours = signal(24);
  timeRanges = [1, 6, 12, 24, 48, 72];

  constructor(
    private http: HttpClient,
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadMetrics();
  }

  getAuthHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Token ${token}`
    });
  }

  loadMetrics(): void {
    this.isLoading.set(true);
    this.error.set(null);

    const token = this.authService.getToken();
    if (!token) {
      this.isLoading.set(false);
      this.error.set('No se encontró token de autenticación. Por favor, inicia sesión.');
      this.router.navigate(['/login']);
      return;
    }

    const headers = this.getAuthHeaders();
    const hours = this.selectedHours();

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
          this.error.set('Acceso denegado. Se requieren privilegios de administrador. Asegúrate de que tu usuario tenga is_staff=True o is_superuser=True.');
        } else if (err.status === 401) {
          this.error.set('Autenticación requerida. Por favor, inicia sesión nuevamente.');
          this.authService.logout();
        } else if (err.status === 0) {
          this.error.set('No se puede conectar al servidor. Asegúrate de que el backend esté ejecutándose en http://127.0.0.1:8000');
        } else if (err.status === 404) {
          this.error.set('Endpoint de monitoreo no encontrado. Por favor, verifica la configuración del backend.');
        } else if (err.status === 500) {
          const detail = err.error?.detail || err.error?.error || 'Error interno del servidor';
          this.error.set(`Error del servidor: ${detail}. Revisa los logs del backend para más detalles.`);
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

  onTimeRangeChange(hours: number): void {
    this.selectedHours.set(hours);
    this.loadMetrics();
  }

  getStatusColor(statusCode: number): string {
    if (statusCode >= 500) return 'text-red-500';
    if (statusCode >= 400) return 'text-orange-500';
    if (statusCode >= 300) return 'text-yellow-500';
    return 'text-green-500';
  }

  getStatusBadgeColor(statusCode: number): string {
    if (statusCode >= 500) return 'bg-red-500/20 text-red-300 border-red-500';
    if (statusCode >= 400) return 'bg-orange-500/20 text-orange-300 border-orange-500';
    if (statusCode >= 300) return 'bg-yellow-500/20 text-yellow-300 border-yellow-500';
    return 'bg-green-500/20 text-green-300 border-green-500';
  }

  formatNumber(num: number): string {
    return num.toLocaleString('es-ES');
  }

  formatTime(ms: number): string {
    if (ms < 1000) return `${ms.toFixed(2)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  }
}

