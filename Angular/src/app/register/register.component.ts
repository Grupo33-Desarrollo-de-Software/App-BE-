// Componente para el formulario de registro
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
  isLoading = signal(false); // Indica si está cargando
  errorMessage = signal<string | null>(null); // Mensaje de error
  successMessage = signal<string | null>(null); // Mensaje de éxito
  selectedFile: File | null = null; // Archivo de foto seleccionado
  previewUrl: string | null = null; // Vista previa de la foto

  constructor(
    private fb: FormBuilder,
    private apiService: ServiceAPI,
    private authService: AuthService,
    private router: Router
  ) {
    // Verifica si el usuario actual es admin
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

    // Solo agregar campos de permiso si el usuario es admin
    if (isAdmin) {
      formControls.is_staff = [false];
      formControls.is_superuser = [false];
    }

    this.registerForm = this.fb.group(formControls, { validators: this.passwordMatchValidator });
  }

  // Verifica si el usuario es admin
  get isAdmin(): boolean {
    return this.authService.checkIsAdmin();
  }

  // Valida que las contraseñas coincidan
  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password');
    const confirmPassword = form.get('confirmPassword');

    if (password && confirmPassword && password.value !== confirmPassword.value) {
      confirmPassword.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    }
    return null;
  }

  // Maneja la selección de un archivo de foto
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const file = input.files[0];

      // Valida que sea una imagen
      if (!file.type.startsWith('image/')) {
        this.errorMessage.set('Please select an image file');
        return;
      }

      // Valida que el tamaño sea menor a 5MB
      if (file.size > 5 * 1024 * 1024) {
        this.errorMessage.set('Image size must be less than 5MB');
        return;
      }

      this.selectedFile = file;

      // Crea una vista previa de la imagen
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.previewUrl = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  // Elimina la foto seleccionada
  removePhoto(): void {
    this.selectedFile = null;
    this.previewUrl = null;
    const fileInput = document.getElementById('foto') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }

  // Obtiene el mensaje de error de un campo
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

  // Verifica si un campo tiene errores
  isFieldInvalid(fieldName: string): boolean {
    const field = this.registerForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }

  // Procesa el envío del formulario de registro
  onSubmit(): void {
    if (this.registerForm.invalid) {
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

    // Solo incluye permisos si el usuario es admin
    if (this.isAdmin) {
      registerData.is_staff = formValue.is_staff || false;
      registerData.is_superuser = formValue.is_superuser || false;
    }

    // Envía los datos al servidor
    this.apiService.register(registerData).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        this.successMessage.set(`Account created successfully! Welcome, ${response.username}!`);

        // Guarda los datos del usuario
        this.authService.setUser(response.token, {
          id: response.id,
          username: response.username,
          is_staff: response.is_staff || false,
          is_superuser: response.is_superuser || false
        });

        // Guarda en el navegador
        localStorage.setItem('auth_token', response.token);
        localStorage.setItem('user_id', response.id.toString());
        localStorage.setItem('username', response.username);

        // Redirige después de 2 segundos
        setTimeout(() => {
          this.router.navigate(['/']);
        }, 2000);
      },
      error: (error) => {
        this.isLoading.set(false);
        if (error.error) {
          // Manejar errores de validación
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

