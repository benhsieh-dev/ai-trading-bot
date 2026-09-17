import { NavLink } from 'react-router-dom';
import './Navigation.css';

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `nav-tab${isActive ? ' active' : ''}`;

function Navigation() {
  return (
    <nav className="navigation-tabs">
      <NavLink to="/dashboard" className={navLinkClass}>
        📈Stock Trading
      </NavLink>
      <NavLink to="/portfolio" className={navLinkClass}>
        📊Portfolio
      </NavLink>
      <NavLink to="/options" className={navLinkClass}>
        🎯Options Trading
      </NavLink>
      <NavLink to="/sentiment" className={navLinkClass}>
        📊Sentiment & Backtesting
      </NavLink>
      <NavLink to="/history" className={navLinkClass}>
        🗂️Trade History (PostgreSQL)
      </NavLink>
    </nav>
  );
}

export default Navigation;