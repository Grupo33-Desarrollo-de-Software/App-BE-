//componente para el formulario de login
//maneja la autenticación de usuarios con validación de formularios
import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { ServiceAPI, LoginRequest } from '../service-api.service';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-login', //selector HTML para usar este componente
  standalone: true, //componente standalone (no necesita módulo)
  imports: [CommonModule, ReactiveFormsModule, RouterModule], //módulos necesarios
  templateUrl: './login.component.html', //template HTML
  styleUrl: './login.component.css' //estilos CSS
})
export class LoginComponent {
  loginForm: FormGroup; //formulario reactivo con validaciones
  isLoading = signal(false); //estado reactivo: indica si está cargando la petición
  errorMessage = signal<string | null>(null); //estado reactivo: mensaje de error a mostrar

  constructor(
    private fb: FormBuilder, //constructor de formularios reactivos
    private apiService: ServiceAPI, //servicio para hacer peticiones al backend
    private authService: AuthService, //servicio de autenticación
    private router: Router //servicio de navegación
  ) {
    //crea el formulario con validaciones
    //username: requerido, mínimo 3 caracteres
    //password: requerido, mínimo 8 caracteres
    this.loginForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(8)]]
    });
  }

  //obtiene el mensaje de error de un campo específico del formulario
  //se usa en el template para mostrar errores de validación
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

  //verifica si un campo del formulario tiene errores y ha sido tocado
  //se usa en el template para mostrar estilos de error
  isFieldInvalid(fieldName: string): boolean {
    const field = this.loginForm.get(fieldName);
    //retorna true si el campo existe, es inválido y ha sido modificado o tocado
    return !!(field && field.invalid && (field.dirty || field.touched));
  }

  //procesa el envío del formulario de login
  //valida el formulario y envía los datos al backend
  onSubmit(): void {
    //si el formulario es inválido, marca todos los campos como tocados para mostrar errores
    if (this.loginForm.invalid) {
      Object.keys(this.loginForm.controls).forEach(key => {
        this.loginForm.get(key)?.markAsTouched();
      });
      return; //no continúa si hay errores
    }

    //activa el estado de carga y limpia errores anteriores
    this.isLoading.set(true);
    this.errorMessage.set(null);

    //obtiene los valores del formulario
    const formValue = this.loginForm.value;
    const loginData: LoginRequest = {
      username: formValue.username,
      password: formValue.password
    };

    //envía los datos de login al servidor
    this.apiService.login(loginData).subscribe({
      //si el login es exitoso
      next: (response) => {
        this.isLoading.set(false);

        //guarda los datos del usuario en el servicio de autenticación
        this.authService.setUser(response.token, {
          id: response.id,
          username: response.username,
          is_staff: response.is_staff,
          is_superuser: response.is_superuser
        });

        //guarda datos adicionales en localStorage (compatibilidad con código antiguo)
        localStorage.setItem('auth_token', response.token);
        localStorage.setItem('user_id', response.id.toString());
        localStorage.setItem('username', response.username);

        //redirige a la página principal (tanto admin como usuario normal)
        if (response.is_staff || response.is_superuser) {
          this.router.navigate(['/']);
        } else {
          this.router.navigate(['/']);
        }
      },
      //si hay un error en el login
      error: (error) => {
        this.isLoading.set(false);
        //procesa diferentes tipos de errores del servidor
        if (error.error) {
          if (typeof error.error === 'object') {
            const errors = error.error;
            //si hay errores generales (no de campo específico)
            if (errors.non_field_errors) {
              this.errorMessage.set(Array.isArray(errors.non_field_errors)
                ? errors.non_field_errors.join(', ')
                : errors.non_field_errors);
            } else {
              this.errorMessage.set('Invalid username or password');
            }
          } else {
            //si el error es un string
            this.errorMessage.set(error.error || 'Login failed. Please try again.');
          }
        } else {
          //si no hay detalles del error
          this.errorMessage.set('Login failed. Please check your credentials and try again.');
        }
      }
    });
  }
}

