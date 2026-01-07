import React from 'react';
import { Row, Col, Card, Button } from 'react-bootstrap';
import { useInventory } from '../context/InventoryContext';

const Home = () => {
  const { products, getBillingHistory } = useInventory();
  const billingHistory = getBillingHistory();

  const totalProducts = products.length;
  const lowStockCount = products.filter((p) => p.stock < 10).length;
  const totalTransactions = billingHistory.length;
  const totalRevenue = billingHistory.reduce((sum, record) => sum + record.total, 0);

  const features = [
    {
      title: 'Inventory Management',
      description: 'Real-time tracking of stock levels with low stock alerts for all items.',
      icon: '📊',
    },
    {
      title: 'Billing & POS',
      description: 'Fast checkout with automatic calculations for subtotals, taxes, and discounts.',
      icon: '💰',
    },
    {
      title: 'Auto-Image Fetching',
      description: 'Automatically fetch product images from the web based on product names.',
      icon: '🖼️',
    },
    {
      title: 'Analytics & Reporting',
      description: 'View sales dashboards and track profit margins with detailed reports.',
      icon: '📊',
    },
  ];

  return (
    <div>
      <Row className="mb-5 mt-5">
        <Col md={12}>
          <div className="text-center">
            <h1 className="display-4 fw-bold mb-3">Welcome to InventroBil Web</h1>
            {/* <p className="lead text-muted mb-4">
              A comprehensive inventory and billing management system for plumbing & electronics shops
            </p> */}
            <Button href="/inventory" variant="primary" size="lg" className="me-3">
              Manage Inventory
            </Button>
            <Button href="/billing" variant="success" size="lg">
              Start Billing
            </Button>
          </div>
        </Col>
      </Row>

      {/* Stats Section */}
      <Row className="mb-5">
        <Col md={3} className="mb-3">
          <Card className="text-center shadow-sm">
            <Card.Body>
              <h3 className="text-primary fw-bold">{totalProducts}</h3>
              <p className="text-muted mb-0">Total Products</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} className="mb-3">
          <Card className="text-center shadow-sm">
            <Card.Body>
              <h3 className="text-warning fw-bold">{lowStockCount}</h3>
              <p className="text-muted mb-0">Low Stock Items</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} className="mb-3">
          <Card className="text-center shadow-sm">
            <Card.Body>
              <h3 className="text-success fw-bold">{totalTransactions}</h3>
              <p className="text-muted mb-0">Transactions Today</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} className="mb-3">
          <Card className="text-center shadow-sm">
            <Card.Body>
              <h3 className="text-info fw-bold">${totalRevenue.toFixed(2)}</h3>
              <p className="text-muted mb-0">Total Revenue</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* <Row className="mb-5">
        {features.map((feature, index) => (
          <Col md={6} lg={3} className="mb-4" key={index}>
            <Card className="h-100 shadow-sm border-0 text-center">
              <Card.Body>
                <div className="fs-1 mb-3">{feature.icon}</div>
                <Card.Title className="fw-bold">{feature.title}</Card.Title>
                <Card.Text className="text-muted">{feature.description}</Card.Text>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row> */}

      {/* <Row>
        <Col md={12}>
          <Card className="bg-light border-0">
            <Card.Body className="text-center py-5">
              <h3 className="mb-3">Ready to manage your shop efficiently?</h3>
              <p className="text-muted mb-4">
                Start using Inventrobil Web to streamline your operations today. All data is stored locally and synced in real-time.
              </p>
              <Button variant="primary" size="lg">
                Get Started Now
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row> */}
    </div>
  );
};

export default Home;