import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Navbar, Nav, Container } from 'react-bootstrap';

const Header = () => {
  const [expanded, setExpanded] = useState(false);

  return (
    <Navbar bg="dark" expand="lg" sticky="top" className="navbar-dark">
      <Container>
        <Navbar.Brand as={Link} to="/" className="fw-bold fs-4">
          InventroBil
        </Navbar.Brand>
        <Navbar.Toggle
          aria-controls="basic-navbar-nav"
          onClick={() => setExpanded(expanded ? false : true)}
        />
        <Navbar.Collapse id="basic-navbar-nav" in={expanded}>
          <Nav className="ms-auto">
            <Nav.Link
              as={Link}
              to="/"
              onClick={() => setExpanded(false)}
              className="mx-2"
            >
              Home
            </Nav.Link>
            <Nav.Link
              as={Link}
              to="/inventory"
              onClick={() => setExpanded(false)}
              className="mx-2"
            >
              Inventory
            </Nav.Link>
            <Nav.Link
              as={Link}
              to="/billing"
              onClick={() => setExpanded(false)}
              className="mx-2"
            >
              Billing
            </Nav.Link>
            <Nav.Link
              as={Link}
              to="/"
              onClick={() => setExpanded(false)}
              className="mx-2"
            >
              [user]
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header;