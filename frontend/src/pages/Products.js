import { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { LayoutDashboard, Package, ShoppingBag, LogOut, Plus, Edit, Trash2, Upload, X } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Button } from '../components/ui/button';

const Products = ({ onLogout }) => {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    price: '',
    description: '',
    colors: '',
    sizes: '',
    stock: '',
    active: true
  });
  const [imageFiles, setImageFiles] = useState([]);
  const [imageUrls, setImageUrls] = useState([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const response = await axios.get(`${API}/admin/products`);
      setProducts(response.data);
    } catch (error) {
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  const handleAddProduct = () => {
    setEditingProduct(null);
    setFormData({
      name: '',
      price: '',
      description: '',
      colors: '',
      sizes: '',
      stock: '',
      active: true
    });
    setImageFiles([]);
    setImageUrls([]);
    setShowModal(true);
  };

  const handleEditProduct = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      price: product.price,
      description: product.description || '',
      colors: product.colors.join(', '),
      sizes: product.sizes.join(', '),
      stock: product.stock,
      active: product.active
    });
    setImageFiles([]);
    setImageUrls(product.images || []);
    setShowModal(true);
  };

  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;

    try {
      await axios.delete(`${API}/admin/products/${productId}`);
      toast.success('Product deleted successfully');
      loadProducts();
    } catch (error) {
      toast.error('Failed to delete product');
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setImageFiles([...imageFiles, ...files]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    setImageFiles([...imageFiles, ...files]);
  };

  const removeImage = (index) => {
    setImageFiles(imageFiles.filter((_, i) => i !== index));
  };

  const removeImageUrl = (index) => {
    setImageUrls(imageUrls.filter((_, i) => i !== index));
  };

  const uploadImages = async () => {
    const uploaded = [];
    for (const file of imageFiles) {
      const formData = new FormData();
      formData.append('file', file);
      try {
        const response = await axios.post(`${API}/admin/upload-image`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        uploaded.push(response.data.url);
      } catch (error) {
        toast.error(`Failed to upload ${file.name}`);
      }
    }
    return uploaded;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);

    try {
      // Upload new images
      const newImageUrls = await uploadImages();
      const allImages = [...imageUrls, ...newImageUrls];

      const payload = {
        name: formData.name,
        price: parseFloat(formData.price),
        description: formData.description,
        colors: formData.colors.split(',').map(c => c.trim()).filter(c => c),
        sizes: formData.sizes.split(',').map(s => s.trim()).filter(s => s),
        stock: parseInt(formData.stock),
        images: allImages,
        active: formData.active
      };

      if (editingProduct) {
        await axios.put(`${API}/admin/products/${editingProduct.product_id}`, payload);
        toast.success('Product updated successfully');
      } else {
        await axios.post(`${API}/admin/products`, payload);
        toast.success('Product created successfully');
      }

      setShowModal(false);
      loadProducts();
    } catch (error) {
      toast.error('Failed to save product');
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="text-lg text-purple-600">Loading...</div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50" data-testid="products-page">
      {/* Header */}
      <header className="glass-effect border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Urban Fashion
            </h1>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              data-testid="logout-button"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 px-4 py-4 text-gray-600 hover:text-purple-600 font-medium"
              data-testid="nav-dashboard"
            >
              <LayoutDashboard className="w-5 h-5" />
              Dashboard
            </button>
            <button
              onClick={() => navigate('/products')}
              className="flex items-center gap-2 px-4 py-4 text-purple-600 border-b-2 border-purple-600 font-semibold"
              data-testid="nav-products"
            >
              <Package className="w-5 h-5" />
              Products
            </button>
            <button
              onClick={() => navigate('/orders')}
              className="flex items-center gap-2 px-4 py-4 text-gray-600 hover:text-purple-600 font-medium"
              data-testid="nav-orders"
            >
              <ShoppingBag className="w-5 h-5" />
              Orders
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Products</h2>
          <Button onClick={handleAddProduct} className="bg-gradient-to-r from-purple-600 to-blue-600 text-white" data-testid="add-product-button">
            <Plus className="w-5 h-5 mr-2" />
            Add Product
          </Button>
        </div>

        {products.length === 0 ? (
          <div className="glass-effect rounded-2xl p-12 text-center">
            <Package className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No products yet</h3>
            <p className="text-gray-500 mb-6">Start by adding your first product</p>
            <Button onClick={handleAddProduct} className="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
              <Plus className="w-5 h-5 mr-2" />
              Add Product
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
              <div key={product.product_id} className="product-card" data-testid="product-card">
                {product.images && product.images.length > 0 ? (
                  <img
                    src={product.images[0]}
                    alt={product.name}
                    className="w-full h-48 object-cover"
                  />
                ) : (
                  <div className="w-full h-48 bg-gradient-to-br from-purple-200 to-blue-200 flex items-center justify-center">
                    <Package className="w-16 h-16 text-purple-400" />
                  </div>
                )}
                <div className="p-4">
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{product.name}</h3>
                  <p className="text-2xl font-bold text-purple-600 mb-3">Rs. {product.price}</p>
                  <div className="space-y-2 mb-4">
                    {product.colors && product.colors.length > 0 && (
                      <p className="text-sm text-gray-600">
                        <span className="font-semibold">Colors:</span> {product.colors.join(', ')}
                      </p>
                    )}
                    {product.sizes && product.sizes.length > 0 && (
                      <p className="text-sm text-gray-600">
                        <span className="font-semibold">Sizes:</span> {product.sizes.join(', ')}
                      </p>
                    )}
                    <p className="text-sm text-gray-600">
                      <span className="font-semibold">Stock:</span> {product.stock}
                    </p>
                    <span className={`status-badge ${product.active ? 'status-delivered' : 'status-cancelled'}`}>
                      {product.active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEditProduct(product)}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                      data-testid="edit-product-button"
                    >
                      <Edit className="w-4 h-4" />
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteProduct(product.product_id)}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                      data-testid="delete-product-button"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Add/Edit Product Modal */}
      <Dialog open={showModal} onOpenChange={setShowModal}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="product-modal">
          <DialogHeader>
            <DialogTitle>{editingProduct ? 'Edit Product' : 'Add New Product'}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4 mt-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Product Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="input-field"
                required
                data-testid="product-name-input"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Price (Rs.)</label>
                <input
                  type="number"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  className="input-field"
                  required
                  data-testid="product-price-input"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Stock</label>
                <input
                  type="number"
                  value={formData.stock}
                  onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                  className="input-field"
                  required
                  data-testid="product-stock-input"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="input-field"
                rows={3}
                data-testid="product-description-input"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Colors (comma-separated)</label>
                <input
                  type="text"
                  value={formData.colors}
                  onChange={(e) => setFormData({ ...formData, colors: e.target.value })}
                  className="input-field"
                  placeholder="Red, Blue, Green"
                  data-testid="product-colors-input"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Sizes (comma-separated)</label>
                <input
                  type="text"
                  value={formData.sizes}
                  onChange={(e) => setFormData({ ...formData, sizes: e.target.value })}
                  className="input-field"
                  placeholder="S, M, L, XL"
                  data-testid="product-sizes-input"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={formData.active}
                onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                className="w-4 h-4 text-purple-600"
                data-testid="product-active-checkbox"
              />
              <label className="text-sm font-semibold text-gray-700">Product Active</label>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Product Images</label>
              
              {/* Existing Images */}
              {imageUrls.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {imageUrls.map((url, index) => (
                    <div key={index} className="relative w-24 h-24">
                      <img src={url} alt="Product" className="w-full h-full object-cover rounded" />
                      <button
                        type="button"
                        onClick={() => removeImageUrl(index)}
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* New Image Previews */}
              {imageFiles.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {imageFiles.map((file, index) => (
                    <div key={index} className="relative w-24 h-24">
                      <img
                        src={URL.createObjectURL(file)}
                        alt="Preview"
                        className="w-full h-full object-cover rounded"
                      />
                      <button
                        type="button"
                        onClick={() => removeImage(index)}
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Upload Area */}
              <div
                className="drag-drop-area"
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                onClick={() => document.getElementById('file-input').click()}
                data-testid="image-upload-area"
              >
                <Upload className="w-12 h-12 mx-auto mb-3 text-purple-600" />
                <p className="text-gray-700 font-semibold mb-1">Click to upload or drag and drop</p>
                <p className="text-sm text-gray-500">PNG, JPG up to 10MB</p>
                <input
                  id="file-input"
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                onClick={() => setShowModal(false)}
                variant="outline"
                className="flex-1"
                data-testid="cancel-button"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={uploading}
                className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white"
                data-testid="save-product-button"
              >
                {uploading ? 'Saving...' : editingProduct ? 'Update Product' : 'Add Product'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Products;