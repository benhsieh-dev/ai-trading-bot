import { Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard';
import { PortfolioComponent } from './components/portfolio/portfolio';
import { OptionsComponent } from './components/options/options';
import {SentimentAnalysisComponent} from './components/sentiment-analysis/sentiment-analysis';

export const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'options', component: OptionsComponent },
  { path: 'portfolio', component: PortfolioComponent },
  { path: 'sentiment', component: SentimentAnalysisComponent },
  { path: '**', redirectTo: '' }
];
