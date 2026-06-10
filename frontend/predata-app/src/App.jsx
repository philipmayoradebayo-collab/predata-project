// App.jsx — PreData Farmer Dashboard
import { useState } from "react"
import axios from "axios"
import "./App.css"

const API = "https://predata-project.onrender.com"

// ── Crop Recommendation Form ──────────────────────────────
function CropAdvisor() {
  const [form, setForm] = useState({
    N: "", P: "", K: "",
    temperature: "", humidity: "",
    ph: "", rainfall: ""
  })
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const handle = e => setForm({ ...form, [e.target.name]: e.target.value })

  const submit = async () => {
    setLoading(true); setError(null); setResult(null)
    try {
      const res = await axios.post(`${API}/predict/crop`, {
        N:           parseFloat(form.N),
        P:           parseFloat(form.P),
        K:           parseFloat(form.K),
        temperature: parseFloat(form.temperature),
        humidity:    parseFloat(form.humidity),
        ph:          parseFloat(form.ph),
        rainfall:    parseFloat(form.rainfall)
      })
      setResult(res.data)
    } catch (e) {
      setError("Could not connect to API. Make sure backend is running.")
    }
    setLoading(false)
  }

  return (
    <div className="card">
      <h2>🌱 Crop & Fertilizer Advisor</h2>
      {["N","P","K"].map(f => (
        <div className="form-group" key={f}>
          <label>{f === "N" ? "Nitrogen (N)" : f === "P" ? "Phosphorus (P)" : "Potassium (K)"} kg/ha</label>
          <input name={f} value={form[f]} onChange={handle} type="number" placeholder="e.g. 90" />
        </div>
      ))}
      <div className="form-group">
        <label>Temperature (°C)</label>
        <input name="temperature" value={form.temperature} onChange={handle} type="number" placeholder="e.g. 27" />
      </div>
      <div className="form-group">
        <label>Humidity (%)</label>
        <input name="humidity" value={form.humidity} onChange={handle} type="number" placeholder="e.g. 80" />
      </div>
      <div className="form-group">
        <label>Soil pH</label>
        <input name="ph" value={form.ph} onChange={handle} type="number" placeholder="e.g. 6.5" />
      </div>
      <div className="form-group">
        <label>Rainfall (mm)</label>
        <input name="rainfall" value={form.rainfall} onChange={handle} type="number" placeholder="e.g. 200" />
      </div>
      <button className="btn" onClick={submit} disabled={loading}>
        {loading ? "Analysing..." : "Get Recommendation"}
      </button>
      {loading && <p className="loading">🤖 AI is analysing your farm data...</p>}
      {error  && <div className="error">{error}</div>}
      {result && (
        <div className="result">
          <h3>Recommended Crop</h3>
          <p className="crop-name">🌾 {result.recommended_crop.toUpperCase()}</p>
          <p>Confidence: <strong>{result.confidence}</strong></p>
          <h3 style={{marginTop:"0.8rem"}}>NPK Fertilizer Guide</h3>
          <div className="npk">
            <span className="npk-badge">N: {result.npk_recommendation.N}</span>
            <span className="npk-badge">P: {result.npk_recommendation.P}</span>
            <span className="npk-badge">K: {result.npk_recommendation.K}</span>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Weather Prediction Form ───────────────────────────────
function WeatherPredictor() {
  const [form, setForm] = useState({
    temp_avg: "", temp_max: "", temp_min: "",
    humidity: "", rainfall: "", solar_radiation: "",
    wind_speed: "", soil_moisture: "",
    month: "", day_of_year: "", is_rainy_season: "1"
  })
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const handle = e => setForm({ ...form, [e.target.name]: e.target.value })

  const submit = async () => {
    setLoading(true); setError(null); setResult(null)
    try {
      const res = await axios.post(`${API}/predict/weather`, {
        temp_avg:        parseFloat(form.temp_avg),
        temp_max:        parseFloat(form.temp_max),
        temp_min:        parseFloat(form.temp_min),
        humidity:        parseFloat(form.humidity),
        rainfall:        parseFloat(form.rainfall),
        solar_radiation: parseFloat(form.solar_radiation),
        wind_speed:      parseFloat(form.wind_speed),
        soil_moisture:   parseFloat(form.soil_moisture),
        month:           parseInt(form.month),
        day_of_year:     parseInt(form.day_of_year),
        is_rainy_season: parseInt(form.is_rainy_season)
      })
      setResult(res.data)
    } catch (e) {
      setError("Could not connect to API. Make sure backend is running.")
    }
    setLoading(false)
  }

  return (
    <div className="card">
      <h2>🌤️ Weather Forecast</h2>
      {[
        ["temp_avg",        "Average Temperature (°C)", "27"],
        ["temp_max",        "Max Temperature (°C)",     "32"],
        ["temp_min",        "Min Temperature (°C)",     "22"],
        ["humidity",        "Humidity (%)",             "80"],
        ["rainfall",        "Rainfall (mm)",            "5"],
        ["solar_radiation", "Solar Radiation (MJ/m²)",  "18"],
        ["wind_speed",      "Wind Speed (m/s)",         "2.5"],
        ["soil_moisture",   "Soil Moisture (mm)",       "3"],
        ["month",           "Month (1-12)",             "6"],
        ["day_of_year",     "Day of Year (1-365)",      "160"],
      ].map(([name, label, placeholder]) => (
        <div className="form-group" key={name}>
          <label>{label}</label>
          <input name={name} value={form[name]} onChange={handle}
                 type="number" placeholder={`e.g. ${placeholder}`} />
        </div>
      ))}
      <div className="form-group">
        <label>Rainy Season?</label>
        <select name="is_rainy_season" value={form.is_rainy_season}
                onChange={handle}
                style={{width:"100%",padding:"0.5rem",borderRadius:"8px",border:"1px solid #ddd"}}>
          <option value="1">Yes</option>
          <option value="0">No</option>
        </select>
      </div>
      <button className="btn" onClick={submit} disabled={loading}>
        {loading ? "Predicting..." : "Predict Weather"}
      </button>
      {loading && <p className="loading">🤖 LSTM model is predicting...</p>}
      {error  && <div className="error">{error}</div>}
      {result && (
        <div className="result">
          <h3>Tomorrow's Forecast</h3>
          <p>🌡️ Predicted Temperature: <strong>{result.predicted_temperature} {result.unit_temperature}</strong></p>
          <p>🌧️ Predicted Rainfall: <strong>{result.predicted_rainfall} {result.unit_rainfall}</strong></p>
        </div>
      )}
    </div>
  )
}


// ── Crop Intelligence Component ──────────────────────────
function CropIntelligence() {
  const [cropName, setCropName] = useState("")
  const [state, setState]       = useState("Nigeria")
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)

  const search = async () => {
    if (!cropName.trim()) return
    setLoading(true); setError(null); setResult(null)
    try {
      const res = await axios.post(`${API}/predict/crop-intelligence`, {
        crop_name: cropName,
        state: state
      })
      setResult(res.data)
    } catch (e) {
      setError("Could not connect to API. Make sure backend is running.")
    }
    setLoading(false)
  }

  return (
    <div className="card" style={{gridColumn: "1 / -1"}}>
      <h2>🔍 Crop Intelligence — Planting & Harvest Guide</h2>
      <div style={{display:"flex", gap:"1rem", marginBottom:"1rem", flexWrap:"wrap"}}>
        <div className="form-group" style={{flex:1, minWidth:"200px"}}>
          <label>Enter Any Crop Name</label>
          <input
            value={cropName}
            onChange={e => setCropName(e.target.value)}
            onKeyDown={e => e.key === "Enter" && search()}
            placeholder="e.g. maize, rice, tomato, cassava..."
            type="text"
          />
        </div>
        <div className="form-group" style={{flex:1, minWidth:"200px"}}>
          <label>Your State</label>
          <select
            value={state}
            onChange={e => setState(e.target.value)}
            style={{width:"100%",padding:"0.5rem",borderRadius:"8px",border:"1px solid #ddd"}}
          >
            {["Nigeria","Abia","Adamawa","AkwaIbom","Anambra","Bauchi",
              "Bayelsa","Benue","Borno","CrossRiver","Delta","Ebonyi",
              "Edo","Ekiti","Enugu","FCT","Gombe","Imo","Jigawa",
              "Kaduna","Kano","Katsina","Kebbi","Kogi","Kwara","Lagos",
              "Nasarawa","Niger","Ogun","Ondo","Osun","Oyo","Plateau",
              "Rivers","Sokoto","Taraba","Yobe","Zamfara"
            ].map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>
      <button className="btn" onClick={search} disabled={loading}>
        {loading ? "Searching..." : "🔍 Get Crop Intelligence"}
      </button>

      {loading && <p className="loading">🤖 AI is fetching crop data...</p>}
      {error   && <div className="error">{error}</div>}

      {result && result.found && (
        <div className="result" style={{marginTop:"1rem"}}>
          <h3 style={{fontSize:"1.3rem"}}>🌾 {result.crop.toUpperCase()} — Complete Guide</h3>

          <div style={{display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))", gap:"1rem", marginTop:"1rem"}}>

            <div style={{background:"#f1f8e9", padding:"1rem", borderRadius:"8px"}}>
              <h4 style={{color:"#2d6a4f", marginBottom:"0.5rem"}}>📅 Planting & Harvest</h4>
              <p><strong>Plant:</strong> {result.data.planting_period}</p>
              <p><strong>Harvest:</strong> {result.data.harvest_period}</p>
              <p><strong>Growing days:</strong> {result.data.growing_days}</p>
            </div>

            <div style={{background:"#e8f5e9", padding:"1rem", borderRadius:"8px"}}>
              <h4 style={{color:"#2d6a4f", marginBottom:"0.5rem"}}>🌡️ Climate Needs</h4>
              <p><strong>Temperature:</strong> {result.data.temperature}</p>
              <p><strong>Rainfall:</strong> {result.data.rainfall_needed}</p>
              <p><strong>Soil:</strong> {result.data.soil_type}</p>
            </div>

            <div style={{background:"#f9fbe7", padding:"1rem", borderRadius:"8px"}}>
              <h4 style={{color:"#2d6a4f", marginBottom:"0.5rem"}}>🧪 Fertilizer Guide</h4>
              <div className="npk" style={{marginBottom:"0.5rem"}}>
                <span className="npk-badge">N: {result.data.fertilizer.N}</span>
                <span className="npk-badge">P: {result.data.fertilizer.P}</span>
                <span className="npk-badge">K: {result.data.fertilizer.K}</span>
              </div>
              <p style={{fontSize:"0.8rem"}}>{result.data.fertilizer.application}</p>
            </div>

            <div style={{background:"#fff8e1", padding:"1rem", borderRadius:"8px"}}>
              <h4 style={{color:"#2d6a4f", marginBottom:"0.5rem"}}>💰 Market Info</h4>
              <p><strong>Yield:</strong> {result.data.yield_per_ha}</p>
              <p><strong>Price:</strong> {result.data.market_price}</p>
            </div>

          </div>

          <div style={{marginTop:"1rem", display:"grid", gridTemplateColumns:"1fr 1fr", gap:"1rem"}}>
            <div style={{background:"#fce4ec", padding:"1rem", borderRadius:"8px"}}>
              <h4 style={{color:"#c62828", marginBottom:"0.5rem"}}>🦠 Diseases & Cures</h4>
              {result.data.common_diseases.map((d, i) => (
                <div key={i} style={{marginBottom:"0.5rem"}}>
                  <p><strong>{d.name}</strong></p>
                  <p style={{fontSize:"0.8rem", color:"#555"}}>💊 {d.cure}</p>
                </div>
              ))}
            </div>

            <div style={{background:"#e8eaf6", padding:"1rem", borderRadius:"8px"}}>
              <h4 style={{color:"#283593", marginBottom:"0.5rem"}}>🐛 Pests & Pesticides</h4>
              {result.data.pesticides.map((p, i) => (
                <div key={i} style={{marginBottom:"0.5rem"}}>
                  <p><strong>{p.pest}</strong></p>
                  <p style={{fontSize:"0.8rem", color:"#555"}}>🧴 {p.pesticide}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {result && !result.found && (
        <div className="error" style={{marginTop:"1rem"}}>
          {result.message}
        </div>
      )}
    </div>
  )
}
export default function App() {
  return (
    <div>
      <nav className="navbar">
        <h1>🌿 PreData — AI Farm Assistant</h1>
        <span>Microclimate Prediction & Nutrient Recommendation</span>
      </nav>

      <div className="container">
        {/* Stats Bar */}
        <div className="stats">
          <div className="stat-card">
            <div className="value">99.55%</div>
            <div className="label">Crop Model Accuracy</div>
          </div>
          <div className="stat-card">
            <div className="value">0.0087</div>
            <div className="label">Weather Model MSE</div>
          </div>
          <div className="stat-card">
            <div className="value">9,861</div>
            <div className="label">Training Records</div>
          </div>
          <div className="stat-card">
            <div className="value">22</div>
            <div className="label">Crops Supported</div>
          </div>
        </div>

        {/* Main Cards */}
        <div className="cards">
  <CropAdvisor />
  <WeatherPredictor />
</div>

{/* Crop Intelligence — Full Width */}
<div className="cards">
  <CropIntelligence />
</div>
      </div>
    </div>
  )
}