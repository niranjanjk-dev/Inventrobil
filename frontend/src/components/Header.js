import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header style={{ backgroundColor: '#282c34', padding: '10px', color: 'white' }}>
      <h1>Inventrobil Web</h1>
      <nav>
        <Link to="/" style={{ margin: '0 10px', color: 'white' }}>Home</Link>
        <Link to="/inventory" style={{ margin: '0 10px', color: 'white' }}>Inventory</Link>
        <Link to="/billing" style={{ margin: '0 10px', color: 'white' }}>Billing</Link>
      </nav>
    </header>
  );
};

export default Header;