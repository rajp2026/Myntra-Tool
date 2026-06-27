import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { UploadCloud, CheckCircle, XCircle, AlertCircle, Package } from 'lucide-react';
import './index.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get(`${API_URL}/history/latest`).then(res => {
      if (res.data && res.data.job_id) {
        setData(res.data);
      }
    }).catch(err => console.log('No history found'));
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const startWebSocket = (jobId) => {
    const ws = new WebSocket(`ws://localhost:8000/ws/scrape/${jobId}`);
    
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      
      setData(prev => {
        const newData = {
          products: prev?.products ? [...prev.products] : [],
          category_ads: prev?.category_ads ? { ...prev.category_ads } : {},
          summary: prev?.summary ? { ...prev.summary } : { total: 0, successful: 0, failed: 0 }
        };
        
        if (msg.type === 'product') {
          newData.products.push(msg.data);
          if (msg.data.status === 'success') newData.summary.successful++;
          else newData.summary.failed++;
          newData.summary.total++;
        } else if (msg.type === 'ad') {
          newData.category_ads[msg.category] = msg.data;
        } else if (msg.type === 'summary') {
          newData.summary = msg.data;
        }
        
        return newData;
      });
    };
    
    ws.onclose = () => {
      setLoading(false);
    };
    
    ws.onerror = (err) => {
      setError('WebSocket error occurred');
      setLoading(false);
    };
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file first.');
      return;
    }

    setLoading(true);
    setError('');
    setData({ products: [], category_ads: {}, summary: { total: 0, successful: 0, failed: 0 } });
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      startWebSocket(response.data.job_id);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during upload.');
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

  const downloadJSON = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `myntra_scrape_${data.job_id || 'results'}.json`;
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

      {!data && loading && (
        <div style={{textAlign: 'center', padding: '4rem'}}>
          <div style={{
            display: 'inline-block', width: '40px', height: '40px', 
            border: '4px solid rgba(78,205,196,0.3)', borderTopColor: 'var(--accent-teal)', 
            borderRadius: '50%', animation: 'spin 1s linear infinite'
          }} />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          <h2>Connecting...</h2>
          <p style={{color: 'var(--text-secondary)'}}>Preparing to scrape data.</p>
        </div>
      )}

      {data && (
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
            <div className="summary-item" style={{marginLeft: 'auto', display: 'flex', gap: '1rem'}}>
              <button className="upload-btn" onClick={downloadJSON}>Download JSON</button>
              <button className="upload-btn" onClick={() => { setData(null); setFile(null); }}>Scrape Another</button>
            </div>
          </div>

          <h2 style={{marginTop: '2rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Package color="var(--accent-teal)" /> Scraped Products 
            {loading && <span style={{fontSize: '0.9rem', color: 'var(--text-secondary)', marginLeft: '1rem', fontStyle: 'italic'}}>Scraping in progress...</span>}
          </h2>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Image</th>
                  <th>Brand</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>Rating</th>
                </tr>
              </thead>
              <tbody>
                {data.products?.map((p, i) => (
                  <tr key={i}>
                    <td>
                      {p.images?.length > 0 ? (
                        <img src={p.images[0]} className="table-img" alt="Product" />
                      ) : (
                        <div className="table-img" style={{background: '#333'}}></div>
                      )}
                    </td>
                    <td className="brand" style={{marginBottom: 0}}>{p.brand}</td>
                    <td>{p.title || 'Unknown Product'}</td>
                    <td className="category" style={{marginBottom: 0}}>{p.category}</td>
                    <td>
                      {p.discounted_price && <div className="price-current">₹{p.discounted_price}</div>}
                      {p.mrp && p.mrp !== p.discounted_price && <div className="price-mrp">₹{p.mrp}</div>}
                    </td>
                    <td>
                      {p.rating && (
                        <div className="rating" style={{marginBottom: 0}}>
                          <CheckCircle size={16} /> {p.rating.toFixed(1)} ({p.ratings_count})
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {Object.keys(data.category_ads || {}).length > 0 && (
            <div style={{marginTop: '4rem'}}>
              <h2 style={{marginBottom: '1rem'}}>Sponsored Category Ads</h2>
              {Object.entries(data.category_ads).map(([cat, ads]) => (
                <div key={cat} style={{marginBottom: '2rem'}}>
                  <h3 style={{color: 'var(--accent-teal)'}}>{cat}</h3>
                  <div className="table-container" style={{marginTop: '1rem'}}>
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Image</th>
                          <th>Brand</th>
                          <th>Name</th>
                          <th>Price</th>
                        </tr>
                      </thead>
                      <tbody>
                        {ads.map((ad, i) => (
                          <tr key={i}>
                            <td>
                              <img src={ad.image} className="table-img" alt="Ad" />
                            </td>
                            <td className="brand" style={{marginBottom: 0}}>{ad.brand}</td>
                            <td>{ad.name}</td>
                            <td><div className="price-current">₹{ad.price}</div></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
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
