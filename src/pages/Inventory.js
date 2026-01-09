import React, { useState, useRef } from 'react';
import { useInventory } from '../context/InventoryContext';
import 'bootstrap/dist/css/bootstrap.min.css';
import './Inventory.css'

const Inventory = () => {
  const {
    products,
    addProduct,
    updateProduct,
    deleteProduct,
    exportInventory,
    importInventory,
  } = useInventory();

  const [search, setSearch] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [alertVariant, setAlertVariant] = useState('success');
  const fileInputRef = useRef(null);
  const alertTimeoutRef = useRef(null);

  const [newProduct, setNewProduct] = useState({
    name: '',
    category: 'Plumbing',
    stock: '',
    price: '',
    sku: '',
  });

  const [editProduct, setEditProduct] = useState(null);

  const filteredProducts = products.filter(
    (product) =>
      product.name.toLowerCase().includes(search.toLowerCase()) ||
      product.sku.toLowerCase().includes(search.toLowerCase())
  );

  const showNotification = (message, variant = 'success') => {
    if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
    setAlertMessage(message);
    setAlertVariant(variant);
    setShowAlert(true);
    alertTimeoutRef.current = setTimeout(() => setShowAlert(false), 2000);
  };

  const handleAddProduct = (e) => {
    e.preventDefault();
    if (newProduct.name && newProduct.stock && newProduct.price && newProduct.sku) {
      try {
        addProduct(newProduct);
        setNewProduct({ name: '', category: 'Plumbing', stock: '', price: '', sku: '' });
        setShowAddForm(false);
        showNotification(`Product "${newProduct.sku}" added successfully!`);
      } catch (error) {
        showNotification(`Error adding product: ${error.message}`, 'danger');
      }
    }
  };

  const handleStartEdit = (product) => {
    setEditingId(product.id);
    setEditProduct({ ...product });
  };

  const handleUpdateProduct = (e) => {
    e.preventDefault();
    if (editProduct) {
      try {
        updateProduct(editingId, editProduct);
        setEditingId(null);
        setEditProduct(null);
        showNotification('Product updated successfully!');
      } catch (error) {
        showNotification(`Error updating product: ${error.message}`, 'danger');
      }
    }
  };

  const handleDeleteProduct = (id, sku) => {
    if (window.confirm(`Are you sure you want to delete "${sku}"?`)) {
      try {
        deleteProduct(id);
        showNotification(`Product "${sku}" deleted successfully!`);
      } catch (error) {
        showNotification(`Error deleting product: ${error.message}`, 'danger');
      }
    }
  };

  const handleExportInventory = () => {
    try {
      const data = exportInventory();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `inventory_${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      URL.revokeObjectURL(url);
      showNotification(`Inventory exported successfully! (${products.length} products)`);
    } catch (error) {
      showNotification(`Error exporting inventory: ${error.message}`, 'danger');
    }
  };

  const handleImportInventory = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target.result);
        importInventory(data);
        showNotification(`Inventory imported successfully! (${data.products.length} products)`);
        if (fileInputRef.current) fileInputRef.current.value = '';
      } catch {
        showNotification('Error importing inventory: Invalid JSON file', 'danger');
      }
    };
    reader.readAsText(file);
  };

  const handleImportClick = () => fileInputRef.current?.click();

  const getStockBadge = (stock) => {
    if (stock < 10) return <span className="badge bg-danger">Low</span>;
    if (stock < 20) return <span className="badge bg-warning text-dark">Medium</span>;
    return <span className="badge bg-success">In Stock</span>;
  };

  return (
    <div className="container-fluid py-4">
      {showAlert && (
        <div className={`alert alert-${alertVariant} alert-dismissible fade show position-fixed bottom-0 end-0 m-3`} role="alert" style={{ zIndex: 1050 }}>
          {alertMessage}
        </div>
      )}

      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Inventory Management</h2>
        <div className="d-flex gap-2">
          <button className="btn btn-secondary rounded" onClick={handleExportInventory}>Export JSON</button>
          <button className="btn btn-secondary rounded" onClick={handleImportClick}>Import JSON</button>
          <button
            className={`btn ${showAddForm ? 'btn-danger' : 'btn-primary'} rounded`}
            onClick={() => setShowAddForm(!showAddForm)}
          >
            {showAddForm ? 'Cancel' : 'Add Product'}
          </button>
          <input type="file" ref={fileInputRef} onChange={handleImportInventory} accept=".json" style={{ display: 'none' }} />
        </div>
      </div>

      {showAddForm && (
        <form className="card shadow-sm mb-4" onSubmit={handleAddProduct}>
          <div className="card-body">
            <h5 className="card-title">Add New Product</h5>
            <div className="row g-3">
              <div className="col-md-6">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Product Name"
                  value={newProduct.name}
                  onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                  required
                />
              </div>
              <div className="col-md-6">
                <input
                  type="text"
                  className="form-control"
                  placeholder="SKU"
                  value={newProduct.sku}
                  onChange={(e) => setNewProduct({ ...newProduct, sku: e.target.value })}
                  required
                />
              </div>
              <div className="col-md-6">
                <select className="form-select" value={newProduct.category} onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })}>
                  <option>Plumbing</option>
                  <option>Electronics</option>
                </select>
              </div>
              <div className="col-md-6">
                <input
                  type="number"
                  className="form-control"
                  placeholder="Stock"
                  value={newProduct.stock}
                  onChange={(e) => setNewProduct({ ...newProduct, stock: e.target.value })}
                  required
                />
              </div>
              <div className="col-md-6">
                <input
                  type="number"
                  className="form-control"
                  placeholder="Price ($)"
                  value={newProduct.price}
                  onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
                  step="0.01"
                  required
                />
              </div>
              <div className="col-md-6">
                <button className="btn btn-primary w-100" type="submit">Save Product</button>
              </div>
            </div>
          </div>
        </form>
      )}

      <div className="input-group mb-4">
        <span className="input-group-text">🔍</span>
        <input
          type="text"
          className="form-control"
          placeholder="Search by name or sku..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <span className="input-group-text">{filteredProducts.length}/{products.length}</span>
      </div>

      <div className="table-responsive">
        <table className="table table-hover table-striped">
          <thead className="table-dark">
            <tr>
              <th>Product Name</th>
              <th>Category</th>
              <th>SKU</th>
              <th>Stock</th>
              <th>Price</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredProducts.length > 0 ? filteredProducts.map(product => (
              <tr key={product.id}>
                <td className='fw-medium'>{product.name}</td>
                <td>{product.category}</td>
                <td><code>{product.sku}</code></td>
                <td>{product.stock}</td>
                <td className='fw-medium'>${product.price.toFixed(2)}</td>
                <td>{getStockBadge(product.stock)}</td>
                <td>
                  <button className="btn btn-sm btn-outline-primary me-2" onClick={() => handleStartEdit(product)}>Edit</button>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => handleDeleteProduct(product.id, product.sku)}>Delete</button>
                </td>
              </tr>
            )) : (
              <tr>
                <td colSpan="7" className="text-center text-muted py-3">No products found</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Edit Modal */}
      {editingId !== null && editProduct && (
        <div className="modal d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Edit Product</h5>
                <button type="button" className="btn-close" onClick={() => setEditingId(null)}></button>
              </div>
              <form onSubmit={handleUpdateProduct}>
                <div className="modal-body">
                  <div className="mb-3">
                    <input type="text" className="form-control" value={editProduct.name} onChange={(e) => setEditProduct({ ...editProduct, name: e.target.value })} />
                  </div>
                  <div className="mb-3">
                    <input type="text" className="form-control" value={editProduct.sku} onChange={(e) => setEditProduct({ ...editProduct, sku: e.target.value })} />
                  </div>
                  <div className="mb-3">
                    <select className="form-select" value={editProduct.category} onChange={(e) => setEditProduct({ ...editProduct, category: e.target.value })}>
                      <option>Plumbing</option>
                      <option>Electronics</option>
                    </select>
                  </div>
                  <div className="mb-3">
                    <input type="number" className="form-control" value={editProduct.stock} onChange={(e) => setEditProduct({ ...editProduct, stock: e.target.value })} />
                  </div>
                  <div className="mb-3">
                    <input type="number" className="form-control" value={editProduct.price} step="0.01" onChange={(e) => setEditProduct({ ...editProduct, price: e.target.value })} />
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setEditingId(null)}>Cancel</button>
                  <button className="btn btn-primary" type="submit">Update Product</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Inventory;