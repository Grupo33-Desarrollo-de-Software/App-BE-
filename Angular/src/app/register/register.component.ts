import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { ServiceAPI, RegisterRequest } from '../service-api.service';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  registerForm: FormGroup;
  isLoading = signal(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);
  selectedFile: File | null = null;
  previewUrl: string | null = null;

  constructor(
    private fb: FormBuilder,
    private apiService: ServiceAPI,
    private authService: AuthService,
    private router: Router
  ) {
    // Check if current user is admin
    const isAdmin = this.authService.checkIsAdmin();
    
    const formControls: any = {
      username: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(150)]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]],
      email: ['', [Validators.email]],
      first_name: ['', [Validators.maxLength(150)]],
      last_name: ['', [Validators.maxLength(150)]],
      bio: ['', [Validators.maxLength(500)]],
      notifPorEmail: [true],
      notifRecomendaciones: [true],
      notifGenerales: [true]
    };

    // Only add permission fields if user is admin
    if (isAdmin) {
      formControls.is_staff = [false];
      formControls.is_superuser = [false];
    }

    this.registerForm = this.fb.group(formControls, { validators: this.passwordMatchValidator });
  }

  // Getter to check if current user is admin
  get isAdmin(): boolean {
    return this.authService.checkIsAdmin();
  }

  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password');
    const confirmPassword = form.get('confirmPassword');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      confirmPassword.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    }
    return null;
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const file = input.files[0];
      
      // Validate file type
      if (!file.type.startsWith('image/')) {
        this.errorMessage.set('Please select an image file');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        this.errorMessage.set('Image size must be less than 5MB');
        return;
      }
      
      this.selectedFile = file;
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.previewUrl = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  removePhoto(): void {
    this.selectedFile = null;
    this.previewUrl = null;
    const fileInput = document.getElementById('foto') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }

  getErrorMessage(fieldName: string): string {
    const field = this.registerForm.get(fieldName);
    if (field?.hasError('required')) {
      return `${fieldName} is required`;
    }
    if (field?.hasError('minlength')) {
      const minLength = field.errors?.['minlength'].requiredLength;
      return `${fieldName} must be at least ${minLength} characters`;
    }
    if (field?.hasError('maxlength')) {
      const maxLength = field.errors?.['maxlength'].requiredLength;
      return `${fieldName} must be less than ${maxLength} characters`;
    }
    if (field?.hasError('email')) {
      return 'Please enter a valid email address';
    }
    if (field?.hasError('passwordMismatch')) {
      return 'Passwords do not match';
    }
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.registerForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }

  onSubmit(): void {
    if (this.registerForm.invalid) {
      // Mark all fields as touched to show errors
      Object.keys(this.registerForm.controls).forEach(key => {
        this.registerForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);
    this.successMessage.set(null);

    const formValue = this.registerForm.value;
    const registerData: RegisterRequest = {
      username: formValue.username,
      password: formValue.password,
      email: formValue.email || undefined,
      first_name: formValue.first_name || undefined,
      last_name: formValue.last_name || undefined,
      bio: formValue.bio || undefined,
      foto: this.selectedFile || undefined,
      notifPorEmail: formValue.notifPorEmail,
      notifRecomendaciones: formValue.notifRecomendaciones,
      notifGenerales: formValue.notifGenerales
    };

    // Only include permission fields if user is admin
    if (this.isAdmin) {
      registerData.is_staff = formValue.is_staff || false;
      registerData.is_superuser = formValue.is_superuser || false;
    }

    this.apiService.register(registerData).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        this.successMessage.set(`Account created successfully! Welcome, ${response.username}!`);
        
        // Guardar datos del usuario en el servicio de autenticación
        this.authService.setUser(response.token, {
          id: response.id,
          username: response.username,
          is_staff: response.is_staff || false,
          is_superuser: response.is_superuser || false
        });

        // También guardar en localStorage para compatibilidad
        localStorage.setItem('auth_token', response.token);
        localStorage.setItem('user_id', response.id.toString());
        localStorage.setItem('username', response.username);
        
        // Redirect after 2 seconds
        setTimeout(() => {
          this.router.navigate(['/']);
        }, 2000);
      },
      error: (error) => {
        this.isLoading.set(false);
        if (error.error) {
          // Handle validation errors from backend
          const errors = error.error;
          if (typeof errors === 'object') {
            const errorMessages = Object.keys(errors).map(key => {
              const fieldErrors = Array.isArray(errors[key]) ? errors[key] : [errors[key]];
              return `${key}: ${fieldErrors.join(', ')}`;
            });
            this.errorMessage.set(errorMessages.join('\n'));
          } else {
            this.errorMessage.set(error.error || 'Registration failed. Please try again.');
          }
        } else {
          this.errorMessage.set('Registration failed. Please try again.');
        }
      }
    });
  }
}

