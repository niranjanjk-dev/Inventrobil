import React, { useState } from 'react';
import {
  Container,
  Row,
  Col,
  Form,
  ListGroup,
  Button,
  Card,
  InputGroup,
  Table,
  Badge,
  Alert,
} from 'react-bootstrap';
import { useInventory } from '../context/InventoryContext';

const Billing = () => {
  const { products, addBillingRecord, updateStock, getBillingHistory } = useInventory();

  const [cart, setCart] = useState([]);
  const [search, setSearch] = useState('');
  const [gstRate] = useState(18);
  const [discountPercent, setDiscountPercent] = useState(0);
  const [billingHistory, setBillingHistory] = useState(getBillingHistory());
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [alertVariant, setAlertVariant] = useState('success');

  const filteredProducts = products.filter(
    (p) =>
      (p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.sku.toLowerCase().includes(search.toLowerCase())) &&
      p.stock > 0
  );

  const showNotification = (message, variant = 'success') => {
    setAlertMessage(message);
    setAlertVariant(variant);
    setShowAlert(true);
    setTimeout(() => setShowAlert(false), 3000);
  };

  const addToCart = (product) => {
    const existingItem = cart.find((item) => item.id === product.id);
    if (existingItem) {
      if (existingItem.quantity < product.stock) {
        setCart(
          cart.map((item) =>
            item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
          )
        );
      } else {
        showNotification(`❌ Cannot add more items. Only ${product.stock} in stock.`, 'warning');
      }
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
      showNotification(`✅ Added "${product.name}" to cart`);
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter((item) => item.id !== productId));
  };

  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId);
    } else {
      const product = products.find((p) => p.id === productId);
      if (product && quantity > product.stock) {
        showNotification(
          `❌ Cannot exceed stock. Only ${product.stock} available.`,
          'warning'
        );
        return;
      }
      setCart(
        cart.map((item) =>
          item.id === productId ? { ...item, quantity } : item
        )
      );
    }
  };

  const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const discountAmount = (subtotal * discountPercent) / 100;
  const subtotalAfterDiscount = subtotal - discountAmount;
  const gstAmount = (subtotalAfterDiscount * gstRate) / 100;
  const total = subtotalAfterDiscount + gstAmount;

  const handleCheckout = () => {
    if (cart.length === 0) {
      showNotification('❌ Cart is empty', 'warning');
      return;
    }

    try {
      // Update stock for each item
      cart.forEach((item) => {
        const currentProduct = products.find((p) => p.id === item.id);
        if (currentProduct) {
          updateStock(item.id, currentProduct.stock - item.quantity);
        }
      });

      // Create billing record
      const billingRecord = {
        items: cart,
        subtotal: subtotal,
        discountPercent: discountPercent,
        discountAmount: discountAmount,
        gstRate: gstRate,
        gstAmount: gstAmount,
        total: total,
      };

      addBillingRecord(billingRecord);

      // Reset cart and show success
      setCart([]);
      setDiscountPercent(0);
      setBillingHistory(getBillingHistory());

      showNotification(`✅ Checkout completed! Total: $${total.toFixed(2)}`);
    } catch (error) {
      showNotification(`❌ Checkout error: ${error.message}`, 'danger');
    }
  };

  const handleClearCart = () => {
    if (cart.length > 0 && window.confirm('Are you sure you want to clear the cart?')) {
      setCart([]);
      setDiscountPercent(0);
    }
  };

  return (
    <Container fluid>
      {showAlert && (
        <Alert
          variant={alertVariant}
          dismissible
          onClose={() => setShowAlert(false)}
          className="mb-3"
        >
          {alertMessage}
        </Alert>
      )}

      <Row className="mb-4">
        <Col md={12}>
          <h2>Billing & POS System</h2>
          <small className="text-muted">
            {billingHistory.length} transactions today
          </small>
        </Col>
      </Row>

      <Row>
        {/* Products Section */}
        <Col md={6} className="mb-4">
          <Card className="shadow-sm">
            <Card.Header className="bg-primary text-white">
              <Card.Title className="mb-0">Products</Card.Title>
            </Card.Header>
            <Card.Body>
              <InputGroup className="mb-3">
                <InputGroup.Text>🔎</InputGroup.Text>
                <Form.Control
                  placeholder="Search products..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </InputGroup>

              {filteredProducts.length > 0 ? (
                <ListGroup
                  className="max-height-500"
                  style={{ maxHeight: '500px', overflowY: 'auto' }}
                >
                  {filteredProducts.map((product) => {
                    const cartItem = cart.find((item) => item.id === product.id);
                    return (
                      <ListGroup.Item
                        key={product.id}
                        className="d-flex justify-content-between align-items-center"
                      >
                        <div>
                          <div className="fw-bold">{product.name}</div>
                          <small className="text-muted">{product.category}</small>
                          <div>
                            <Badge bg="info">${product.price.toFixed(2)}</Badge>
                            <Badge bg="light" text="dark" className="ms-2">
                              Stock: {product.stock}
                            </Badge>
                            {cartItem && (
                              <Badge bg="success" className="ms-2">
                                In Cart: {cartItem.quantity}
                              </Badge>
                            )}
                          </div>
                        </div>
                        <Button
                          variant="success"
                          size="sm"
                          onClick={() => addToCart(product)}
                        >
                          Add
                        </Button>
                      </ListGroup.Item>
                    );
                  })}
                </ListGroup>
              ) : (
                <div className="text-center py-5 text-muted">
                  No products found or no stock available
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        {/* Bill Section */}
        <Col md={6} className="mb-4">
          <Card className="shadow-sm">
            <Card.Header className="bg-success text-white">
              <Card.Title className="mb-0">Current Bill</Card.Title>
            </Card.Header>
            <Card.Body>
              {cart.length > 0 ? (
                <>
                  <Table hover className="mb-3">
                    <thead className="table-light">
                      <tr>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Price</th>
                        <th>Total</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {cart.map((item) => (
                        <tr key={item.id}>
                          <td className="fw-bold">{item.name}</td>
                          <td>
                            <InputGroup size="sm" style={{ width: '70px' }}>
                              <Button
                                variant="outline-danger"
                                size="sm"
                                onClick={() =>
                                  updateQuantity(item.id, item.quantity - 1)
                                }
                              >
                                −
                              </Button>
                              <Form.Control
                                type="number"
                                value={item.quantity}
                                onChange={(e) =>
                                  updateQuantity(
                                    item.id,
                                    parseInt(e.target.value) || 1
                                  )
                                }
                                className="text-center"
                              />
                              <Button
                                variant="outline-success"
                                size="sm"
                                onClick={() =>
                                  updateQuantity(item.id, item.quantity + 1)
                                }
                              >
                                +
                              </Button>
                            </InputGroup>
                          </td>
                          <td>${item.price.toFixed(2)}</td>
                          <td className="fw-bold">
                            ${(item.price * item.quantity).toFixed(2)}
                          </td>
                          <td>
                            <Button
                              variant="outline-danger"
                              size="sm"
                              onClick={() => removeFromCart(item.id)}
                            >
                              remove
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>

                  <hr />

                  <div className="mb-3">
                    <div className="d-flex justify-content-between mb-2">
                      <span>Subtotal:</span>
                      <strong>${subtotal.toFixed(2)}</strong>
                    </div>
                    <div className="d-flex justify-content-between mb-2">
                      <span>
                        Discount:
                        <InputGroup
                          size="sm"
                          className="d-inline-flex ms-2"
                          style={{ width: '100px' }}
                        >
                          <Form.Control
                            type="number"
                            value={discountPercent}
                            onChange={(e) =>
                              setDiscountPercent(
                                Math.max(0, parseInt(e.target.value) || 0)
                              )
                            }
                            step="1"
                          />
                          <InputGroup.Text>%</InputGroup.Text>
                        </InputGroup>
                      </span>
                      <strong>-${discountAmount.toFixed(2)}</strong>
                    </div>
                    <div className="d-flex justify-content-between mb-2">
                      <span>GST ({gstRate}%):</span>
                      <strong>${gstAmount.toFixed(2)}</strong>
                    </div>
                  </div>

                  <Card className="bg-light">
                    <Card.Body className="text-center py-3">
                      <h5 className="mb-2">Grand Total</h5>
                      <h2 className="text-success fw-bold">
                        ${total.toFixed(2)}
                      </h2>
                    </Card.Body>
                  </Card>

                  <div className="mt-3 d-grid gap-2">
                    <Button
                      variant="success"
                      size="lg"
                      className="mb-2"
                      onClick={handleCheckout}
                    >
                      Checkout
                    </Button>
                    <Button
                      variant="outline-danger"
                      onClick={handleClearCart}
                    >
                      Clear Cart
                    </Button>
                  </div>
                </>
              ) : (
                <div className="text-center py-5 text-muted">
                  <p>No items in cart</p>
                  <p>Add products to get started</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Billing;
