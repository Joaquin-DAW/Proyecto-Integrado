import { Routes } from '@angular/router';
import { authGuard, directionGuard, mustChangePasswordGuard } from './core/guards/auth.guard';
import { LayoutComponent } from './shared/components/layout.component';
import { LoginComponent } from './features/auth/login.component';
import { ForgotPasswordComponent } from './features/auth/forgot-password.component';
import { ResetPasswordComponent } from './features/auth/reset-password.component';
import { DashboardComponent } from './features/schedule/dashboard.component';
import { MyAbsencesComponent } from './features/absences/my-absences.component';
import { AllAbsencesComponent } from './features/absences/all-absences.component';
import { ReportsComponent } from './features/reports/reports.component';
import { UsersComponent } from './features/users/users.component';
import { ImportScheduleComponent } from './features/schedule/import-schedule.component';
import { ChangePasswordComponent } from './features/auth/change-password.component';
import { ScheduleSearchComponent } from './features/schedule/schedule-search.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'reset-password', component: ResetPasswordComponent },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'change-password', component: ChangePasswordComponent },
      { path: 'dashboard', component: DashboardComponent, canActivate: [mustChangePasswordGuard] },
      { path: 'absences', component: MyAbsencesComponent, canActivate: [mustChangePasswordGuard] },
      // Pantallas de gestion: solo direccion puede entrar aqui.
      { path: 'absences/all', component: AllAbsencesComponent, canActivate: [mustChangePasswordGuard, directionGuard] },
      { path: 'reports', component: ReportsComponent, canActivate: [mustChangePasswordGuard, directionGuard] },
      { path: 'users', component: UsersComponent, canActivate: [mustChangePasswordGuard, directionGuard] },
      { path: 'schedule/import', component: ImportScheduleComponent, canActivate: [mustChangePasswordGuard, directionGuard] },
      { path: 'schedule/search', component: ScheduleSearchComponent, canActivate: [mustChangePasswordGuard, directionGuard] },
    ],
  },
  { path: '**', redirectTo: '' },
];
