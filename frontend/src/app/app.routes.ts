import { Routes } from '@angular/router';
import { DashboardComponent} from './components/dashboard/dashboard';
import { PortfolioComponent} from './components/portfolio/portfolio';

export const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'portfolio', component: PortfolioComponent },
  { path: '**', redirectTo: '' }
];
