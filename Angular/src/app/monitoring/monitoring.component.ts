import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';

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
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadMetrics();
  }

  getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('auth_token');
    return new HttpHeaders({
      'Authorization': `Token ${token}`
    });
  }

  loadMetrics(): void {
    this.isLoading.set(true);
    this.error.set(null);

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
        if (err.status === 403) {
          this.error.set('Access denied. Admin privileges required.');
        } else if (err.status === 401) {
          this.error.set('Authentication required. Please log in.');
          this.router.navigate(['/login']);
        } else {
          this.error.set('Failed to load monitoring data. Please try again.');
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
    return num.toLocaleString();
  }

  formatTime(ms: number): string {
    if (ms < 1000) return `${ms.toFixed(2)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  }
}

