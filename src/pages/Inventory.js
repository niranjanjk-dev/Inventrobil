import React, { useState, useRef } from 'react';
import { useInventory } from '../context/InventoryContext';
import './Inventory.css';

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
    if (stock < 10) return <span className="badge badge-danger">Low</span>;
    if (stock < 20) return <span className="badge badge-warning">Medium</span>;
    return <span className="badge badge-success">In Stock</span>;
  };

  return (
    <div className="inventory-container">
      {showAlert && (
        <div className={`alert ${alertVariant}`}>
          {alertMessage}
        </div>
      )}

      <div className="inventory-header">
        <h2>Inventory Management</h2>
        <div className="inventory-actions">
          <button className="btn btn-secondary" onClick={handleExportInventory}>Export JSON</button>
          <button className="btn btn-secondary" onClick={handleImportClick}>Import JSON</button>
          <button
            className={`btn ${showAddForm ? 'btn-cancel' : 'btn-primary'}`}
            onClick={() => setShowAddForm(!showAddForm)}
          >
            {showAddForm ? 'Cancel' : 'Add Product'}
          </button>
          <input type="file" ref={fileInputRef} onChange={handleImportInventory} accept=".json" style={{ display: 'none' }} />
        </div>
      </div>

      {showAddForm && (
        <form className="form-card" onSubmit={handleAddProduct}>
          <h4>Add New Product</h4>
          <div className="form-grid">
            <input
              type="text"
              placeholder="Product Name"
              value={newProduct.name}
              onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="SKU"
              value={newProduct.sku}
              onChange={(e) => setNewProduct({ ...newProduct, sku: e.target.value })}
              required
            />
            <select value={newProduct.category} onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })}>
              <option>Plumbing</option>
              <option>Electronics</option>
            </select>
            <input
              type="number"
              placeholder="Stock"
              value={newProduct.stock}
              onChange={(e) => setNewProduct({ ...newProduct, stock: e.target.value })}
              required
            />
            <input
              type="number"
              placeholder="Price ($)"
              value={newProduct.price}
              onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
              step="0.01"
              required
            />
          </div>
          <button className="btn btn-primary w-full" type="submit">Save Product</button>
        </form>
      )}

      <div className="inventory-search">
        <span className="searchIcon">🔍</span>
        <input
          type="text"
          placeholder="Search by name or sku..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <span className="product-count">{filteredProducts.length}/{products.length}</span>
      </div>

      <div className="inventory-table-wrapper">
        <table className="inventory-table striped">
          <thead>
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
                <td className='product-name'>{product.name}</td>
                <td>{product.category}</td>
                <td className="sku-column">{product.sku}</td>
                <td>{product.stock}</td>
                <td className='price-column'>${product.price.toFixed(2)}</td>
                <td>{getStockBadge(product.stock)}</td>
                <td className="actions-column">
                  <button className="btn-edit" onClick={() => handleStartEdit(product)}>Edit</button>
                  <button className="btn-delete" onClick={() => handleDeleteProduct(product.id, product.sku)}>Delete</button>
                </td>
              </tr>
            )) : (
              <tr>
                <td colSpan="7" className="no-products">No products found</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Edit Modal */}
      {editingId !== null && editProduct && (
        <div className="modal-overlay" onClick={() => setEditingId(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h4>Edit Product</h4>
            <form onSubmit={handleUpdateProduct}>
              <input type="text" value={editProduct.name} onChange={(e) => setEditProduct({ ...editProduct, name: e.target.value })} />
              <input type="text" value={editProduct.sku} onChange={(e) => setEditProduct({ ...editProduct, sku: e.target.value })} />
              <select value={editProduct.category} onChange={(e) => setEditProduct({ ...editProduct, category: e.target.value })}>
                <option>Plumbing</option>
                <option>Electronics</option>
              </select>
              <input type="number" value={editProduct.stock} onChange={(e) => setEditProduct({ ...editProduct, stock: e.target.value })} />
              <input type="number" value={editProduct.price} step="0.01" onChange={(e) => setEditProduct({ ...editProduct, price: e.target.value })} />
              <button className="btn btn-primary w-full" type="submit">Update Product</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Inventory;