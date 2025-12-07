# -Clinical-Research-AI-Assistant
AI-powered protocol generation and site selection for clinical trials

import React, { useState } from 'react';
import { FileText, Building2, Loader2, Download, Mail, CheckCircle, AlertCircle } from 'lucide-react';

const ClinicalResearchApp = () => {
  const [activeTab, setActiveTab] = useState('protocol');
  const [loading, setLoading] = useState(false);
  const [protocolData, setProtocolData] = useState(null);
  const [siteData, setSiteData] = useState(null);
  
  // Protocol Generator State
  const [studyIdea, setStudyIdea] = useState('');
  
  // Site Selector State
  const [targetPatients, setTargetPatients] = useState(60);

  const sites = [
    { id: "S1", country: "India", patients: 80, trials: 4, edc: "Yes", days: 45 },
    { id: "S2", country: "Singapore", patients: 40, trials: 2, edc: "Yes", days: 30 },
    { id: "S3", country: "Malaysia", patients: 60, trials: 5, edc: "No", days: 55 },
    { id: "S4", country: "Thailand", patients: 35, trials: 1, edc: "Yes", days: 25 }
  ];

  const generateProtocol = async () => {
    if (!studyIdea.trim()) {
      alert('Please enter a study idea');
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          messages: [
            {
              role: "user",
              content: `Write a concise clinical trial protocol for: ${studyIdea}

Include these sections:
1. Title
2. Objective
3. Study Design
4. Population
5. Primary Endpoint
6. Sample Size

Keep it clear and professional. Mark assumptions with ⚠️.`
            }
          ],
        })
      });

      const data = await response.json();
      const text = data.content.find(c => c.type === "text")?.text || "Protocol generation failed";
      
      setProtocolData({
        text,
        timestamp: new Date().toLocaleString()
      });
    } catch (error) {
      setProtocolData({
        text: `⚠️ [Offline Template]\n\nStudy Idea: ${studyIdea}\n\n1. Title: [Insert Title]\n2. Objective: [Primary goal]\n3. Study Design: [e.g., Randomized, placebo-controlled]\n4. Population: [Eligible participants]\n5. Primary Endpoint: [Measurement target]\n6. Sample Size: [Number of participants]`,
        timestamp: new Date().toLocaleString()
      });
    }
    
    setLoading(false);
  };

  const rankSites = async () => {
    setLoading(true);

    // Calculate scores
    const rankedSites = sites.map(site => {
      const capacityScore = (site.patients - 35) / (80 - 35) * 0.4;
      const speedScore = (1 - (site.days - 25) / (55 - 25)) * 0.3;
      const edcScore = (site.edc === "Yes" ? 1 : 0) * 0.2;
      const activeScore = (1 - (site.trials - 1) / (5 - 1)) * 0.1;
      
      return {
        ...site,
        score: ((capacityScore + speedScore + edcScore + activeScore) * 100).toFixed(1)
      };
    }).sort((a, b) => b.score - a.score);

    const topSite = rankedSites[0];

    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          messages: [
            {
              role: "user",
              content: `Write a professional email to research site ${topSite.id} in ${topSite.country} asking if they can enroll ${targetPatients} patients for a clinical study. Keep it polite and concise (3-4 sentences). Include a subject line.`
            }
          ],
        })
      });

      const data = await response.json();
      const emailText = data.content.find(c => c.type === "text")?.text || "Email generation failed";
      
      setSiteData({
        sites: rankedSites,
        topSite,
        email: emailText,
        timestamp: new Date().toLocaleString()
      });
    } catch (error) {
      setSiteData({
        sites: rankedSites,
        topSite,
        email: `Subject: Clinical Study Enrollment Inquiry\n\nDear ${topSite.id} Team,\n\nWe are initiating a clinical study and your site has been identified as a strong candidate. We plan to enroll approximately ${targetPatients} eligible patients and would like to confirm your site's capacity and expected enrollment timeline.\n\nBest regards,\nClinical Operations Team`,
        timestamp: new Date().toLocaleString()
      });
    }

    setLoading(false);
  };

  const downloadProtocol = () => {
    const blob = new Blob([protocolData.text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'protocol.txt';
    a.click();
  };

  const downloadSites = () => {
    const csv = [
      'Rank,Site_ID,Country,Score,Monthly_Patients,Avg_Enrollment_Days,EDC_Experience,Active_Trials',
      ...siteData.sites.map((s, i) => 
        `${i+1},${s.id},${s.country},${s.score},${s.patients},${s.days},${s.edc},${s.trials}`
      )
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ranked_sites.csv';
    a.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🏥 Clinical Research AI Assistant
          </h1>
          <p className="text-gray-600">
            AI-powered protocol generation and site selection for clinical trials
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-lg mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('protocol')}
              className={`flex-1 py-4 px-6 font-medium transition-colors ${
                activeTab === 'protocol'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <FileText className="inline mr-2" size={20} />
              Protocol Generator
            </button>
            <button
              onClick={() => setActiveTab('sites')}
              className={`flex-1 py-4 px-6 font-medium transition-colors ${
                activeTab === 'sites'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <Building2 className="inline mr-2" size={20} />
              Site Selector
            </button>
          </div>

          <div className="p-6">
            {activeTab === 'protocol' && (
              <div>
                <h2 className="text-xl font-semibold text-gray-800 mb-4">
                  Generate Clinical Trial Protocol
                </h2>
                
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Study Idea
                  </label>
                  <textarea
                    value={studyIdea}
                    onChange={(e) => setStudyIdea(e.target.value)}
                    placeholder="Enter your clinical study idea here... (e.g., 'A phase 3 trial to evaluate the efficacy of Drug X in treating hypertension')"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={4}
                  />
                </div>

                <button
                  onClick={generateProtocol}
                  disabled={loading}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? (
                    <>
                      <Loader2 className="inline mr-2 animate-spin" size={20} />
                      Generating...
                    </>
                  ) : (
                    'Generate Protocol'
                  )}
                </button>

                {protocolData && (
                  <div className="mt-6 bg-gray-50 rounded-lg p-6 border border-gray-200">
                    <div className="flex justify-between items-center mb-4">
                      <div className="flex items-center text-green-600">
                        <CheckCircle className="mr-2" size={20} />
                        <span className="font-medium">Protocol Generated</span>
                      </div>
                      <button
                        onClick={downloadProtocol}
                        className="flex items-center text-blue-600 hover:text-blue-800"
                      >
                        <Download className="mr-2" size={18} />
                        Download
                      </button>
                    </div>
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono bg-white p-4 rounded border border-gray-200">
                      {protocolData.text}
                    </pre>
                    <p className="text-xs text-gray-500 mt-2">
                      Generated at {protocolData.timestamp}
                    </p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'sites' && (
              <div>
                <h2 className="text-xl font-semibold text-gray-800 mb-4">
                  Rank Research Sites
                </h2>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Patient Enrollment
                  </label>
                  <input
                    type="number"
                    value={targetPatients}
                    onChange={(e) => setTargetPatients(parseInt(e.target.value) || 60)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    min={1}
                  />
                </div>

                <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-medium text-gray-800 mb-3">Available Sites</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-blue-100">
                        <tr>
                          <th className="p-2 text-left">Site ID</th>
                          <th className="p-2 text-left">Country</th>
                          <th className="p-2 text-right">Patients/Month</th>
                          <th className="p-2 text-right">Active Trials</th>
                          <th className="p-2 text-center">EDC</th>
                          <th className="p-2 text-right">Avg Days</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white">
                        {sites.map(site => (
                          <tr key={site.id} className="border-b">
                            <td className="p-2 font-medium">{site.id}</td>
                            <td className="p-2">{site.country}</td>
                            <td className="p-2 text-right">{site.patients}</td>
                            <td className="p-2 text-right">{site.trials}</td>
                            <td className="p-2 text-center">{site.edc}</td>
                            <td className="p-2 text-right">{site.days}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <button
                  onClick={rankSites}
                  disabled={loading}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? (
                    <>
                      <Loader2 className="inline mr-2 animate-spin" size={20} />
                      Analyzing...
                    </>
                  ) : (
                    'Rank Sites'
                  )}
                </button>

                {siteData && (
                  <div className="mt-6 space-y-6">
                    <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                      <div className="flex justify-between items-center mb-4">
                        <div className="flex items-center text-green-600">
                          <CheckCircle className="mr-2" size={20} />
                          <span className="font-medium">Sites Ranked</span>
                        </div>
                        <button
                          onClick={downloadSites}
                          className="flex items-center text-blue-600 hover:text-blue-800"
                        >
                          <Download className="mr-2" size={18} />
                          Download CSV
                        </button>
                      </div>

                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead className="bg-gray-200">
                            <tr>
                              <th className="p-2 text-left">Rank</th>
                              <th className="p-2 text-left">Site</th>
                              <th className="p-2 text-left">Country</th>
                              <th className="p-2 text-right">Score</th>
                              <th className="p-2 text-right">Patients</th>
                              <th className="p-2 text-right">Days</th>
                              <th className="p-2 text-center">EDC</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white">
                            {siteData.sites.map((site, idx) => (
                              <tr key={site.id} className={`border-b ${idx === 0 ? 'bg-yellow-50' : ''}`}>
                                <td className="p-2 font-bold">{idx + 1}</td>
                                <td className="p-2 font-medium">{site.id}</td>
                                <td className="p-2">{site.country}</td>
                                <td className="p-2 text-right font-semibold text-blue-600">{site.score}</td>
                                <td className="p-2 text-right">{site.patients}</td>
                                <td className="p-2 text-right">{site.days}</td>
                                <td className="p-2 text-center">{site.edc}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      <div className="mt-4 bg-yellow-50 border-l-4 border-yellow-400 p-4">
                        <p className="font-medium text-yellow-800">
                          🏆 Top Site: {siteData.topSite.id} ({siteData.topSite.country}) - Score: {siteData.topSite.score}
                        </p>
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                      <div className="flex items-center text-gray-800 mb-4">
                        <Mail className="mr-2" size={20} />
                        <span className="font-medium">Suggested Email</span>
                      </div>
                      <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono bg-white p-4 rounded border border-gray-200">
                        {siteData.email}
                      </pre>
                    </div>

                    <p className="text-xs text-gray-500">
                      Analysis completed at {siteData.timestamp}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-600 text-sm">
          <p>Powered by Claude AI • Clinical Research Assistant</p>
        </div>
      </div>
    </div>
  );
};

export default ClinicalResearchApp;
