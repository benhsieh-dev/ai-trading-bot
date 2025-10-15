import { Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard';
import { PortfolioComponent } from './components/portfolio/portfolio';
import { OptionsComponent } from './components/options/options';

export const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'portfolio', component: PortfolioComponent },
  { path: 'options', component: OptionsComponent },
  { path: '**', redirectTo: '' }
];
