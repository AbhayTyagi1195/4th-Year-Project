import React, { useRef, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const getTumorInformation = (prediction = '', confidence = 0) => {
  const p = prediction.toLowerCase();
  let tumorType = 'notumor';
  if (p.includes('glioma')) tumorType = 'glioma';
  else if (p.includes('meningioma')) tumorType = 'meningioma';
  else if (p.includes('pituitary')) tumorType = 'pituitary';

  const map = {
    glioma: {
      name: 'Glioma Tumor',
      color: 'danger',
      icon: '⚠️',
      severity: 'High Risk',
      description: 'Possible glioma pattern detected.'
    },
    meningioma: {
      name: 'Meningioma Tumor',
      color: 'warning',
      icon: '⚡',
      severity: 'Moderate Risk',
      description: 'Possible meningioma pattern detected.'
    },
    pituitary: {
      name: 'Pituitary Tumor',
      color: 'info',
      icon: '🔬',
      severity: 'Moderate Risk',
      description: 'Possible pituitary tumor pattern detected.'
    },
    notumor: {
      name: 'No Tumor Detected',
      color: 'success',
      icon: '✅',
      severity: 'Low Risk',
      description: 'No tumor-like pattern detected.'
    }
  };

  let confidenceLevel = 'Low Confidence';
  if (confidence >= 90) confidenceLevel = 'Very High Confidence';
  else if (confidence >= 70) confidenceLevel = 'High Confidence';
  else if (confidence >= 50) confidenceLevel = 'Moderate Confidence';

  return { ...map[tumorType], confidenceLevel };
};

export default function BrainTumorAnalysis({ user, token, apiBaseUrl }) {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [activeTab, setActiveTab] = useState('upload');
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [imagePreview, setImagePreview] = useState(null);

  const [loading, setLoading] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  const [chartsLoading, setChartsLoading] = useState(false);

  const [error, setError] = useState('');
  const [apiResponse, setApiResponse] = useState(null);
  const [debugResponse, setDebugResponse] = useState(null);
  const [batchResults, setBatchResults] = useState(null);
  const [history, setHistory] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [systemInfo, setSystemInfo] = useState(null);
  const [chartsData, setChartsData] = useState(null);
  const [statisticsData, setStatisticsData] = useState(null);

  const authHeaders = { Authorization: `Bearer ${token}` };

  const clearSingle = () => {
    setSelectedFile(null);
    setImagePreview(null);
    setApiResponse(null);
    setDebugResponse(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    setError('');
    if (!file) return;
    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = (ev) => setImagePreview(ev.target?.result);
    reader.readAsDataURL(file);
    setApiResponse(null);
    setDebugResponse(null);
  };

  const handleMultipleFileSelect = (e) => {
    setSelectedFiles(Array.from(e.target.files || []));
    setBatchResults(null);
    setError('');
  };

  const handleApiPredict = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('image', selectedFile);
      const { data } = await axios.post(`${apiBaseUrl}/api/brain_tumor/predict`, formData, {
        headers: { ...authHeaders, 'Content-Type': 'multipart/form-data' }
      });

      const confidence = data.confidence_percentage ?? (data.confidence || 0) * 100;
      const tumorInfo = getTumorInformation(data.prediction, Number(confidence));
      setApiResponse({ ...data, confidence_percentage: Number(confidence), tumorInfo });
    } catch (err) {
      setError(err?.response?.data?.error || err.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDebugPredict = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('image', selectedFile);
      const { data } = await axios.post(
        `${apiBaseUrl}/api/brain_tumor/debug/prediction`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setDebugResponse(data);
    } catch (err) {
      setError(err?.response?.data?.error || err.message || 'Debug failed');
    } finally {
      setLoading(false);
    }
  };

  const handleBatchPredict = async () => {
    if (!selectedFiles.length) return;
    setBatchLoading(true);
    setError('');
    try {
      const formData = new FormData();
      selectedFiles.forEach((f) => formData.append('images', f));
      const { data } = await axios.post(
        `${apiBaseUrl}/api/brain_tumor/predict/batch`,
        formData,
        { headers: { ...authHeaders, 'Content-Type': 'multipart/form-data' } }
      );
      setBatchResults(data);
    } catch (err) {
      setError(err?.response?.data?.error || err.message || 'Batch prediction failed');
    } finally {
      setBatchLoading(false);
    }
  };

  const loadHistoryAndAnalytics = async () => {
    setError('');
    try {
      const [h, a] = await Promise.all([
        axios.get(`${apiBaseUrl}/api/brain_tumor/history`, { headers: authHeaders }),
        axios.get(`${apiBaseUrl}/api/brain_tumor/analytics`, { headers: authHeaders })
      ]);
      setHistory(h.data?.history || h.data?.predictions || []);
      setAnalytics(a.data);
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed loading history/analytics');
    }
  };

  const loadSystemInfo = async () => {
    setError('');
    try {
      const [health, classes, model] = await Promise.all([
        axios.get(`${apiBaseUrl}/api/health`),
        axios.get(`${apiBaseUrl}/api/brain_tumor/classes`),
        axios.get(`${apiBaseUrl}/api/brain_tumor/model/info`)
      ]);
      setSystemInfo({ health: health.data, classes: classes.data, model: model.data });
    } catch {
      setError('Failed loading system info');
    }
  };

  const loadCharts = async () => {
    setChartsLoading(true);
    setError('');
    try {
      const [charts, stats] = await Promise.all([
        axios.get(`${apiBaseUrl}/api/brain_tumor/results/charts`, { headers: authHeaders }),
        axios.get(`${apiBaseUrl}/api/brain_tumor/results/statistics`, { headers: authHeaders })
      ]);
      setChartsData(charts.data);
      setStatisticsData(stats.data);
    } catch {
      setError('Failed loading charts/statistics');
    } finally {
      setChartsLoading(false);
    }
  };

  const downloadSingleReport = async () => {
    if (!apiResponse) return;
    try {
      setLoading(true);
      const payload = {
        username: user?.username,
        prediction: apiResponse.prediction,
        confidence: apiResponse.confidence_percentage ?? (apiResponse.confidence || 0) * 100,
        image_path: apiResponse.image_path || selectedFile?.name
      };
      const response = await axios.post(
        `${apiBaseUrl}/api/brain_tumor/predict/report`,
        payload,
        { headers: { ...authHeaders, 'Content-Type': 'application/json' }, responseType: 'blob' }
      );
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `brain_tumor_report_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      setError('Failed generating single report');
    } finally {
      setLoading(false);
    }
  };

  const downloadBatchReport = async () => {
    if (!batchResults?.results?.length) return;
    try {
      setBatchLoading(true);
      const payload = {
        username: user?.username,
        results: batchResults.results.map((r) => ({
          filename: r.filename,
          prediction: r.prediction,
          confidence: r.confidence_percentage ?? (r.confidence_score || 0) * 100,
          image_path: r.image_path
        }))
      };
      const response = await axios.post(
        `${apiBaseUrl}/api/brain_tumor/batch/report`,
        payload,
        { headers: { ...authHeaders, 'Content-Type': 'application/json' }, responseType: 'blob' }
      );
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `brain_tumor_batch_report_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      setError('Failed generating batch report');
    } finally {
      setBatchLoading(false);
    }
  };

  return (
    <div className="container py-4 disease-page">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h3 className="mb-0">🧠 Brain Tumor Analysis</h3>
          <small className="text-muted">Authenticated module</small>
        </div>
        <button className="btn btn-outline-secondary" onClick={() => navigate('/dashboard')}>
          ← Back to Dashboard
        </button>
      </div>

      <ul className="nav nav-pills mb-3">
        <li className="nav-item"><button className={`nav-link ${activeTab === 'upload' ? 'active' : ''}`} onClick={() => setActiveTab('upload')}>Single</button></li>
        <li className="nav-item"><button className={`nav-link ${activeTab === 'batch' ? 'active' : ''}`} onClick={() => setActiveTab('batch')}>Batch</button></li>
        <li className="nav-item"><button className={`nav-link ${activeTab === 'history' ? 'active' : ''}`} onClick={() => { setActiveTab('history'); loadHistoryAndAnalytics(); }}>History</button></li>
        <li className="nav-item"><button className={`nav-link ${activeTab === 'results' ? 'active' : ''}`} onClick={() => { setActiveTab('results'); loadCharts(); }}>Results</button></li>
        <li className="nav-item"><button className={`nav-link ${activeTab === 'system' ? 'active' : ''}`} onClick={() => { setActiveTab('system'); loadSystemInfo(); }}>System</button></li>
      </ul>

      {error && <div className="alert alert-danger py-2">{error}</div>}

      {activeTab === 'upload' && (
        <div className="row g-3">
          <div className="col-lg-5">
            <div className="card shadow-sm">
              <div className="card-header">Upload MRI Image</div>
              <div className="card-body">
                <input ref={fileInputRef} type="file" className="form-control mb-3" accept="image/*" onChange={handleFileSelect} />
                {imagePreview && <img src={imagePreview} alt="preview" className="img-fluid rounded border mb-3" style={{ maxHeight: 260 }} />}
                <div className="d-grid gap-2">
                  <button className="btn btn-danger" onClick={handleApiPredict} disabled={loading || !selectedFile}>
                    {loading ? 'Analyzing...' : 'Analyze'}
                  </button>
                  <button className="btn btn-warning" onClick={handleDebugPredict} disabled={loading || !selectedFile}>
                    Debug Predict
                  </button>
                  <button className="btn btn-secondary" onClick={clearSingle}>Clear</button>
                </div>
              </div>
            </div>
          </div>

          <div className="col-lg-7">
            {apiResponse && (
              <div className="card shadow-sm mb-3">
                <div className={`card-header bg-${apiResponse.tumorInfo.color} text-white`}>
                  {apiResponse.tumorInfo.icon} {apiResponse.tumorInfo.name}
                </div>
                <div className="card-body">
                  <p className="mb-2">{apiResponse.tumorInfo.description}</p>
                  <div className="row">
                    <div className="col-md-6">
                      <div className="border rounded p-2 mb-2">
                        <small className="text-muted d-block">Prediction</small>
                        <strong>{apiResponse.prediction}</strong>
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="border rounded p-2 mb-2">
                        <small className="text-muted d-block">Confidence</small>
                        <strong>{Number(apiResponse.confidence_percentage || 0).toFixed(2)}%</strong>
                      </div>
                    </div>
                  </div>
                  <div className="d-grid">
                    <button className="btn btn-success" onClick={downloadSingleReport} disabled={loading}>
                      Download PDF Report
                    </button>
                  </div>
                </div>
              </div>
            )}

            {debugResponse && (
              <div className="card shadow-sm">
                <div className="card-header bg-warning">Debug Response</div>
                <div className="card-body">
                  <pre className="small mb-0" style={{ maxHeight: 260, overflow: 'auto' }}>
                    {JSON.stringify(debugResponse, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'batch' && (
        <div className="card shadow-sm">
          <div className="card-header">Batch Analysis</div>
          <div className="card-body">
            <input type="file" className="form-control mb-3" accept="image/*" multiple onChange={handleMultipleFileSelect} />
            <div className="d-flex gap-2 mb-3">
              <button className="btn btn-danger" onClick={handleBatchPredict} disabled={batchLoading || !selectedFiles.length}>
                {batchLoading ? 'Processing...' : `Analyze ${selectedFiles.length || 0} Images`}
              </button>
              <button className="btn btn-secondary" onClick={() => { setSelectedFiles([]); setBatchResults(null); }}>
                Clear
              </button>
            </div>

            {batchResults && (
              <>
                <div className="alert alert-info">
                  Total: <strong>{batchResults.total_images || batchResults.results?.length || 0}</strong>
                </div>
                <div className="table-responsive">
                  <table className="table table-sm table-bordered">
                    <thead>
                      <tr>
                        <th>Filename</th>
                        <th>Prediction</th>
                        <th>Confidence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(batchResults.results || []).map((r, i) => (
                        <tr key={i}>
                          <td>{r.filename}</td>
                          <td>{r.prediction}</td>
                          <td>{(r.confidence_percentage ?? (r.confidence_score || 0) * 100).toFixed?.(2) || r.confidence_percentage}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <button className="btn btn-success" onClick={downloadBatchReport} disabled={batchLoading}>
                  Download Batch PDF Report
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {activeTab === 'history' && (
        <div className="row g-3">
          <div className="col-lg-6">
            <div className="card shadow-sm">
              <div className="card-header">Analytics Summary</div>
              <div className="card-body">
                <pre className="small mb-0" style={{ maxHeight: 300, overflow: 'auto' }}>
                  {JSON.stringify(analytics, null, 2)}
                </pre>
              </div>
            </div>
          </div>
          <div className="col-lg-6">
            <div className="card shadow-sm">
              <div className="card-header">Prediction History</div>
              <div className="card-body">
                <pre className="small mb-0" style={{ maxHeight: 300, overflow: 'auto' }}>
                  {JSON.stringify(history, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'results' && (
        <div className="card shadow-sm">
          <div className="card-header">Charts & Statistics</div>
          <div className="card-body">
            {chartsLoading ? (
              <p className="mb-0">Loading charts...</p>
            ) : (
              <>
                {chartsData?.charts && (
                  <div className="row">
                    {Object.entries(chartsData.charts).map(([name, b64]) => (
                      <div key={name} className="col-md-6 mb-3">
                        <h6>{name}</h6>
                        <img src={`data:image/png;base64,${b64}`} alt={name} className="img-fluid border rounded" />
                      </div>
                    ))}
                  </div>
                )}
                <h6>Statistics</h6>
                <pre className="small mb-0" style={{ maxHeight: 250, overflow: 'auto' }}>
                  {JSON.stringify(statisticsData, null, 2)}
                </pre>
              </>
            )}
          </div>
        </div>
      )}

      {activeTab === 'system' && (
        <div className="card shadow-sm">
          <div className="card-header">System Information</div>
          <div className="card-body">
            <pre className="small mb-0" style={{ maxHeight: 400, overflow: 'auto' }}>
              {JSON.stringify(systemInfo, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}