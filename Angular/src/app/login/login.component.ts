import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { ServiceAPI, LoginRequest } from '../service-api.service';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  loginForm: FormGroup;
  isLoading = signal(false);
  errorMessage = signal<string | null>(null);

  constructor(
    private fb: FormBuilder,
    private apiService: ServiceAPI,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(8)]]
    });
  }

  getErrorMessage(fieldName: string): string {
    const field = this.loginForm.get(fieldName);
    if (field?.hasError('required')) {
      return `${fieldName} is required`;
    }
    if (field?.hasError('minlength')) {
      const minLength = field.errors?.['minlength'].requiredLength;
      return `${fieldName} must be at least ${minLength} characters`;
    }
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.loginForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      // Mark all fields as touched to show errors
      Object.keys(this.loginForm.controls).forEach(key => {
        this.loginForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    const formValue = this.loginForm.value;
    const loginData: LoginRequest = {
      username: formValue.username,
      password: formValue.password
    };

    this.apiService.login(loginData).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        
        // Guardar datos del usuario en el servicio de autenticación
        this.authService.setUser(response.token, {
          id: response.id,
          username: response.username,
          is_staff: response.is_staff,
          is_superuser: response.is_superuser
        });

        // También guardar en localStorage para compatibilidad
        localStorage.setItem('auth_token', response.token);
        localStorage.setItem('user_id', response.id.toString());
        localStorage.setItem('username', response.username);

        // Redirigir según si es admin o no
        if (response.is_staff || response.is_superuser) {
          this.router.navigate(['/']);
        } else {
          this.router.navigate(['/']);
        }
      },
      error: (error) => {
        this.isLoading.set(false);
        if (error.error) {
          if (typeof error.error === 'object') {
            const errors = error.error;
            if (errors.non_field_errors) {
              this.errorMessage.set(Array.isArray(errors.non_field_errors) 
                ? errors.non_field_errors.join(', ') 
                : errors.non_field_errors);
            } else {
              this.errorMessage.set('Invalid username or password');
            }
          } else {
            this.errorMessage.set(error.error || 'Login failed. Please try again.');
          }
        } else {
          this.errorMessage.set('Login failed. Please check your credentials and try again.');
        }
      }
    });
  }
}

