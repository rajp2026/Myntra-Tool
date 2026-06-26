import React, { useState } from 'react';
import axios from 'axios';
import { UploadCloud, CheckCircle, XCircle, AlertCircle, Package } from 'lucide-react';
import './index.css';

const API_URL = 'http://localhost:8000/upload';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file first.');
      return;
    }

    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(API_URL, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during upload.');
    } finally {
      setLoading(false);
    }
  };

  const downloadSample = () => {
    const csv = "product_id\n35512522\n27356632\n";
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_products.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app-container">
      <header>
        <h1>Myntra Scraper</h1>
        <button onClick={downloadSample} className="upload-btn" style={{marginTop: 0, background: 'transparent', border: '1px solid var(--accent-teal)', color: 'var(--accent-teal)'}}>
          Sample CSV
        </button>
      </header>

      {!data && !loading && (
        <div className="upload-zone" onClick={() => document.getElementById('fileUpload').click()}>
          <UploadCloud size={48} color="var(--accent-teal)" style={{marginBottom: '1rem'}} />
          <h2>{file ? file.name : 'Click or Drag CSV here'}</h2>
          <p style={{color: 'var(--text-secondary)'}}>Upload a CSV file containing 'product_id' column</p>
          <input 
            type="file" 
            id="fileUpload" 
            accept=".csv" 
            style={{display: 'none'}} 
            onChange={handleFileChange} 
          />
          <button 
            className="upload-btn" 
            onClick={(e) => { e.stopPropagation(); handleUpload(); }}
            disabled={!file}
          >
            Start Scraping
          </button>
          {error && <p style={{color: 'var(--accent-coral)', marginTop: '1rem'}}><AlertCircle size={16} inline /> {error}</p>}
        </div>
      )}

      {loading && (
        <div style={{textAlign: 'center', padding: '4rem'}}>
          <div style={{
            display: 'inline-block', width: '40px', height: '40px', 
            border: '4px solid rgba(78,205,196,0.3)', borderTopColor: 'var(--accent-teal)', 
            borderRadius: '50%', animation: 'spin 1s linear infinite'
          }} />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          <h2>Scraping Data...</h2>
          <p style={{color: 'var(--text-secondary)'}}>This might take a moment.</p>
        </div>
      )}

      {data && !loading && (
        <div>
          <div className="summary">
            <div className="summary-item">
              <div className="summary-val">{data.summary?.total || 0}</div>
              <div className="summary-label">Total Products</div>
            </div>
            <div className="summary-item">
              <div className="summary-val" style={{color: 'var(--accent-teal)'}}>{data.summary?.successful || 0}</div>
              <div className="summary-label">Successful</div>
            </div>
            <div className="summary-item">
              <div className="summary-val" style={{color: 'var(--accent-coral)'}}>{data.summary?.failed || 0}</div>
              <div className="summary-label">Failed</div>
            </div>
            <div className="summary-item" style={{marginLeft: 'auto'}}>
              <button className="upload-btn" onClick={() => { setData(null); setFile(null); }}>Scrape Another</button>
            </div>
          </div>

          <h2 style={{marginTop: '2rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Package color="var(--accent-teal)" /> Scraped Products
          </h2>
          <div className="products-grid">
            {data.products?.map((p, i) => (
              <div className="card" key={i}>
                {p.images?.length > 0 && (
                  <div className="card-images">
                    {p.images.slice(0, 2).map((img, j) => <img src={img} key={j} alt="Product" />)}
                  </div>
                )}
                <div className="card-body">
                  <div className="brand">{p.brand}</div>
                  <h3 className="title">{p.title || 'Unknown Product'}</h3>
                  <div className="category">{p.category}</div>
                  {p.rating && (
                    <div className="rating">
                      <CheckCircle size={16} /> {p.rating.toFixed(1)} ({p.ratings_count})
                    </div>
                  )}
                  <div className="price">
                    {p.discounted_price && <span className="price-current">₹{p.discounted_price}</span>}
                    {p.mrp && p.mrp !== p.discounted_price && <span className="price-mrp">₹{p.mrp}</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {Object.keys(data.category_ads || {}).length > 0 && (
            <div style={{marginTop: '4rem'}}>
              <h2 style={{marginBottom: '1rem'}}>Sponsored Category Ads</h2>
              {Object.entries(data.category_ads).map(([cat, ads]) => (
                <div key={cat} style={{marginBottom: '2rem'}}>
                  <h3 style={{color: 'var(--accent-teal)'}}>{cat}</h3>
                  <div className="products-grid" style={{marginTop: '1rem'}}>
                    {ads.map((ad, i) => (
                      <div className="card" key={i} style={{display: 'flex', height: '120px'}}>
                        <img src={ad.image} alt="Ad" style={{width: '100px', objectFit: 'cover'}} />
                        <div className="card-body" style={{padding: '1rem', flex: 1}}>
                          <div className="brand">{ad.brand}</div>
                          <div style={{fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{ad.name}</div>
                          <div style={{marginTop: '0.5rem', fontWeight: 'bold'}}>₹{ad.price}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
