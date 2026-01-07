import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import { InventoryProvider } from './context/InventoryContext';
import Header from './components/Header';
import Home from './pages/Home';
import Inventory from './pages/Inventory';
import Billing from './pages/Billing';
import './App.css';

function App() {
  return (
    <InventoryProvider>
      <Router>
        <div className="App d-flex flex-column min-vh-100">
          <Header />
          <Container as="main" className="flex-grow-1 py-4">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/inventory" element={<Inventory />} />
              <Route path="/billing" element={<Billing />} />
            </Routes>
          </Container>
        </div>
      </Router>
    </InventoryProvider>
  );
}

export default App;
