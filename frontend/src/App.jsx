import React, { useState, useEffect } from 'react';
import {
  ShieldCheck, GitBranch, UploadCloud, Award, BarChart3, Users, LogOut,
  Sparkles, PlusCircle, Trash2, RefreshCw, Code2, ExternalLink, Clock,
  UserCog, Layers, ArrowRight, Compass
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend
} from 'recharts';
import { apiFetch } from './api';

const LEVEL_LABELS = ['0 · Not Demonstrated', '1 · Beginner', '2 · Developing', '3 · Proficient', '4 · Advanced'];

const STATUS_BADGES = {
  'assessment-validated': { label: 'Assessment-Validated', cls: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40' },
  'project-supported': { label: 'Project-Supported', cls: 'bg-sky-500/15 text-sky-300 border-sky-500/40' },
  'claimed': { label: 'Claimed (Unverified)', cls: 'bg-amber-500/15 text-amber-300 border-amber-500/40' },
  'missing': { label: 'Missing Evidence', cls: 'bg-slate-800 text-slate-400 border-slate-700' }
};

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('sg_token') || '');
  const [userRole, setUserRole] = useState(localStorage.getItem('sg_role') || 'student');
  const [authMode, setAuthMode] = useState('login');
  const [authForm, setAuthForm] = useState({
    name: '', email: '', password: '', role: 'student',
    education: 'B.Tech Computer Science', institution: 'Kaizen Institute of Technology', target_role: 'Backend Developer'
  });
  const [authError, setAuthError] = useState('');
  const [loading, setLoading] = useState(false);

  const [activeTab, setActiveTab] = useState('dashboard');
  const [overview, setOverview] = useState(null);
  const [facultyData, setFacultyData] = useState(null);
  const [toast, setToast] = useState(null);

  const [repoUrl, setRepoUrl] = useState('');
  const [repoConsent, setRepoConsent] = useState(true);
  const [submittingEvidence, setSubmittingEvidence] = useState(false);
  const [claimSkill, setClaimSkill] = useState('Docker & Cloud Deployment');
  const [claimNotes, setClaimNotes] = useState('');

  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [assessmentCode, setAssessmentCode] = useState('');
  const [assessmentResult, setAssessmentResult] = useState(null);

  const [profileForm, setProfileForm] = useState(null);
  const [mentorForm, setMentorForm] = useState({ student_id: '', evidence_title: '', comment: '', endorsement_tag: 'Verified Engineering Quality' });

  const notify = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4500);
  };

  const loadData = async () => {
    if (!token) return;
    setLoading(true);
    try {
      if (userRole === 'faculty') {
        const fData = await apiFetch('/faculty/insights');
        setFacultyData(fData);
        if (fData.students?.length && !mentorForm.student_id) {
          setMentorForm(prev => ({
            ...prev,
            student_id: fData.students[0].id,
            evidence_title: fData.students[0].evidence?.[0]?.title || 'Overall Skill Profile'
          }));
        }
      } else {
        const data = await apiFetch('/student/overview');
        setOverview(data);
        setProfileForm({
          name: data.user.name,
          education: data.user.education,
          institution: data.user.institution,
          target_role: data.user.target_role,
          faculty_consent: Boolean(data.user.faculty_consent)
        });
        if (data.available_assessments?.length && !selectedAssessment) {
          setSelectedAssessment(data.available_assessments[0]);
          setAssessmentCode(data.available_assessments[0].starter_code);
        }
      }
    } catch (err) {
      if (err.message.includes('Session') || err.message.includes('Authorization')) {
        handleLogout();
      } else {
        notify(err.message, 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [token, userRole]);

  const handleLogin = async (email, password) => {
    setAuthError('');
    setLoading(true);
    try {
      const res = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });
      localStorage.setItem('sg_token', res.token);
      localStorage.setItem('sg_role', res.user.role);
      setToken(res.token);
      setUserRole(res.user.role);
      setActiveTab(res.user.role === 'faculty' ? 'faculty' : 'dashboard');
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setAuthError('');
    setLoading(true);
    try {
      const res = await apiFetch('/auth/register', {
        method: 'POST',
        body: JSON.stringify(authForm)
      });
      localStorage.setItem('sg_token', res.token);
      localStorage.setItem('sg_role', authForm.role);
      setToken(res.token);
      setUserRole(authForm.role);
      setActiveTab(authForm.role === 'faculty' ? 'faculty' : 'dashboard');
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await apiFetch('/auth/logout', { method: 'POST' }).catch(() => {});
    localStorage.removeItem('sg_token');
    localStorage.removeItem('sg_role');
    setToken('');
    setOverview(null);
    setFacultyData(null);
  };

  const submitGitHub = async (e) => {
    e.preventDefault();
    if (!repoUrl.trim()) return;
    setSubmittingEvidence(true);
    try {
      const res = await apiFetch('/evidence/github', {
        method: 'POST',
        body: JSON.stringify({ repo_url: repoUrl.trim(), consent_confirmed: repoConsent })
      });
      notify(res.result.summary);
      setRepoUrl('');
      await loadData();
    } catch (err) {
      notify(err.message, 'error');
    } finally {
      setSubmittingEvidence(false);
    }
  };

  const submitFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSubmittingEvidence(true);
    try {
      const fd = new FormData();
      fd.append('file', file);
      const res = await apiFetch('/evidence/upload', { method: 'POST', body: fd });
      notify(res.result.summary);
      await loadData();
    } catch (err) {
      notify(err.message, 'error');
    } finally {
      setSubmittingEvidence(false);
      e.target.value = '';
    }
  };

  const submitClaim = async (e) => {
    e.preventDefault();
    setSubmittingEvidence(true);
    try {
      await apiFetch('/evidence/claim', {
        method: 'POST',
        body: JSON.stringify({ skill_name: claimSkill, notes: claimNotes })
      });
      notify(`Added self-declared skill: ${claimSkill} (capped at Level 1 until verified).`);
      setClaimNotes('');
      await loadData();
    } catch (err) {
      notify(err.message, 'error');
    } finally {
      setSubmittingEvidence(false);
    }
  };

  const deleteEvidence = async (id) => {
    try {
      await apiFetch(`/evidence/${id}`, { method: 'DELETE' });
      notify('Evidence removed and skill profile recalculated.');
      await loadData();
    } catch (err) {
      notify(err.message, 'error');
    }
  };

  const submitAssessment = async () => {
    if (!selectedAssessment) return;
    setSubmittingEvidence(true);
    try {
      const res = await apiFetch('/assessments/submit', {
        method: 'POST',
        body: JSON.stringify({ assessment_id: selectedAssessment.id, submitted_code: assessmentCode })
      });
      setAssessmentResult(res);
      notify(res.feedback, res.passed ? 'success' : 'error');
      await loadData();
    } catch (err) {
      notify(err.message, 'error');
    } finally {
      setSubmittingEvidence(false);
    }
  };

  const toggleTaskStatus = async (task) => {
    const order = ['pending', 'in_progress', 'completed'];
    const next = order[(order.indexOf(task.status) + 1) % order.length];
    try {
      await apiFetch(`/roadmap/${task.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: next })
      });
      await loadData();
    } catch (err) {
      notify(err.message, 'error');
    }
  };

  const saveProfile = async (e) => {
    e.preventDefault();
    try {
      await apiFetch('/user/profile', {
        method: 'PUT',
        body: JSON.stringify(profileForm)
      });
      notify('Profile and target career role updated.');
      await loadData();
    } catch (err) {
      notify(err.message, 'error');
    }
  };

  const submitMentorReview = async (e) => {
    e.preventDefault();
    try {
      await apiFetch('/faculty/feedback', {
        method: 'POST',
        body: JSON.stringify({ ...mentorForm, student_id: Number(mentorForm.student_id) })
      });
      notify('Mentor feedback published to student profile.');
      setMentorForm(prev => ({ ...prev, comment: '' }));
    } catch (err) {
      notify(err.message, 'error');
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-obsidian flex flex-col justify-center items-center p-6">
        <div className="max-w-4xl w-full grid md:grid-cols-2 gap-8 bg-surface border border-slate-800 rounded-2xl p-8 shadow-2xl">
          <div className="flex flex-col justify-between space-y-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold tracking-wide">
                <ShieldCheck className="w-4 h-4" /> TEAM KAIZEN · MVP PROTOTYPE
              </div>
              <h1 className="mt-4 text-3xl font-bold tracking-tight text-white">SkillGraph</h1>
              <p className="mt-1 text-sky-400 font-medium">Students list skills. We check the evidence.</p>
              <p className="mt-4 text-sm text-slate-400 leading-relaxed">
                An evidence-based skill intelligence platform that inspects live GitHub repositories, project archives, PDF design docs, and practical coding assessments to generate explainable proficiency levels (0–4) and role-readiness roadmaps.
              </p>
            </div>

            <div className="space-y-3 bg-obsidian/70 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Instant Judge & Evaluator Access
              </div>
              <button
                onClick={() => handleLogin('alex.rivera@kaizen.edu', 'Kaizen2026!')}
                disabled={loading}
                className="w-full flex items-center justify-between px-4 py-3 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-sm transition"
              >
                <span className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4" /> One-Click Judge Student Demo (Alex Rivera)
                </span>
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleLogin('dr.mehta@kaizen.edu', 'Mentor2026!')}
                disabled={loading}
                className="w-full flex items-center justify-between px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm transition"
              >
                <span className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-emerald-400" /> Faculty & Placement Mentor View
                </span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="bg-card/60 border border-slate-800 rounded-xl p-6">
            <div className="flex gap-2 mb-6 border-b border-slate-800 pb-3">
              <button
                onClick={() => setAuthMode('login')}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium ${authMode === 'login' ? 'bg-sky-500/20 text-sky-300' : 'text-slate-400'}`}
              >
                Sign In
              </button>
              <button
                onClick={() => setAuthMode('register')}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium ${authMode === 'register' ? 'bg-sky-500/20 text-sky-300' : 'text-slate-400'}`}
              >
                Create Account
              </button>
            </div>

            {authError && (
              <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/40 text-rose-300 text-xs">
                {authError}
              </div>
            )}

            {authMode === 'login' ? (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleLogin(authForm.email, authForm.password);
                }}
                className="space-y-4"
              >
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Email Address</label>
                  <input
                    type="email"
                    required
                    value={authForm.email}
                    onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
                    placeholder="alex.rivera@kaizen.edu"
                    className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm focus:border-sky-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Password</label>
                  <input
                    type="password"
                    required
                    value={authForm.password}
                    onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
                    placeholder="••••••••"
                    className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm focus:border-sky-500 outline-none"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-sm transition"
                >
                  {loading ? 'Authenticating...' : 'Sign In to SkillGraph'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleRegister} className="space-y-3">
                <input
                  required
                  placeholder="Full Name"
                  value={authForm.name}
                  onChange={(e) => setAuthForm({ ...authForm, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                />
                <input
                  type="email"
                  required
                  placeholder="University / Work Email"
                  value={authForm.email}
                  onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                />
                <input
                  type="password"
                  required
                  placeholder="Password (min 6 chars)"
                  value={authForm.password}
                  onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                />
                <div className="grid grid-cols-2 gap-2">
                  <input
                    placeholder="Degree / Program"
                    value={authForm.education}
                    onChange={(e) => setAuthForm({ ...authForm, education: e.target.value })}
                    className="px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-xs"
                  />
                  <input
                    placeholder="Institution"
                    value={authForm.institution}
                    onChange={(e) => setAuthForm({ ...authForm, institution: e.target.value })}
                    className="px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-xs"
                  />
                </div>
                <select
                  value={authForm.target_role}
                  onChange={(e) => setAuthForm({ ...authForm, target_role: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                >
                  <option value="Backend Developer">Target Role: Backend Developer</option>
                  <option value="Full-Stack Engineer">Target Role: Full-Stack Engineer</option>
                  <option value="AI & Backend Systems Engineer">Target Role: AI & Backend Systems Engineer</option>
                </select>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-sm transition"
                >
                  Register & Initialize Skill Profile
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (userRole === 'faculty' && facultyData) {
    return (
      <div className="min-h-screen bg-obsidian text-slate-100">
        <header className="border-b border-slate-800 bg-surface/90 backdrop-blur sticky top-0 z-20 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
            <div>
              <span className="font-bold text-lg tracking-tight">SkillGraph</span>
              <span className="ml-2 text-xs px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                Faculty & Placement Insights
              </span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-slate-400">{facultyData.viewer}</span>
            <button onClick={handleLogout} className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700">
              <LogOut className="w-3.5 h-3.5" /> Sign Out
            </button>
          </div>
        </header>

        {toast && (
          <div className="fixed bottom-5 right-5 z-50 px-4 py-3 rounded-xl bg-emerald-600 text-white text-sm shadow-xl">
            {toast.msg}
          </div>
        )}

        <main className="max-w-7xl mx-auto p-6 space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-surface border border-slate-800 rounded-2xl p-6">
              <h2 className="text-base font-semibold text-white mb-1">Aggregate Cohort Skill-Gap Bottlenecks</h2>
              <p className="text-xs text-slate-400 mb-4">Comparing verified cohort average against Industry Level 3.0 benchmark</p>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={facultyData.aggregate_gaps} layout="vertical" margin={{ left: 30 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                    <XAxis type="number" domain={[0, 4]} stroke="#94A3B8" fontSize={11} />
                    <YAxis dataKey="skill_name" type="category" width={145} stroke="#CBD5E1" fontSize={11} />
                    <Tooltip contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155' }} />
                    <Bar dataKey="cohort_avg_level" name="Verified Cohort Avg" fill="#38BDF8" radius={[0, 4, 4, 0]} />
                    <Bar dataKey="cohort_gap" name="Gap to Benchmark" fill="#F59E0B" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-surface border border-slate-800 rounded-2xl p-6">
              <h2 className="text-base font-semibold text-white mb-1">Submit Mentor Review & Evidence Endorsement</h2>
              <p className="text-xs text-slate-400 mb-4">Feedback appears directly on the student's verified profile</p>
              <form onSubmit={submitMentorReview} className="space-y-3">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Select Consented Student</label>
                  <select
                    value={mentorForm.student_id}
                    onChange={(e) => setMentorForm({ ...mentorForm, student_id: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                  >
                    {facultyData.students.map(s => (
                      <option key={s.id} value={s.id}>{s.name} — {s.target_role}</option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Reviewed Artifact</label>
                    <input
                      value={mentorForm.evidence_title}
                      onChange={(e) => setMentorForm({ ...mentorForm, evidence_title: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Placement Endorsement Tag</label>
                    <input
                      value={mentorForm.endorsement_tag}
                      onChange={(e) => setMentorForm({ ...mentorForm, endorsement_tag: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Mentor Technical Feedback</label>
                  <textarea
                    required
                    rows={3}
                    value={mentorForm.comment}
                    onChange={(e) => setMentorForm({ ...mentorForm, comment: e.target.value })}
                    placeholder="Comment on architecture quality, test coverage, or readiness..."
                    className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                  />
                </div>
                <button type="submit" className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-sm">
                  Publish Mentor Review
                </button>
              </form>
            </div>
          </div>

          <div className="bg-surface border border-slate-800 rounded-2xl p-6">
            <h2 className="text-base font-semibold text-white mb-4">Placement-Oriented Student Evidence Summaries (Permission-Scoped)</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {facultyData.students.map(st => (
                <div key={st.id} className="bg-obsidian border border-slate-800 rounded-xl p-5 space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-white">{st.name}</h3>
                      <p className="text-xs text-slate-400">{st.education} · {st.institution}</p>
                    </div>
                    <span className="px-2.5 py-1 rounded-full text-xs bg-sky-500/15 text-sky-300 border border-sky-500/30">
                      Target: {st.target_role}
                    </span>
                  </div>
                  <div className="flex gap-4 text-xs text-slate-300">
                    <span>Verified Skills: <strong>{st.verified_skills_count}/8</strong></span>
                    <span>Avg Proficiency: <strong>{st.average_proficiency} / 4.0</strong></span>
                    <span>Evidence Artifacts: <strong>{st.evidence.length}</strong></span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {st.skills.filter(sk => sk.proficiency_level > 0).map(sk => (
                      <span key={sk.skill_name} className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">
                        {sk.skill_name}: L{sk.proficiency_level} ({sk.evidence_status})
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="min-h-screen bg-obsidian flex items-center justify-center text-slate-400 text-sm">
        <RefreshCw className="w-5 h-5 animate-spin mr-2 text-sky-400" /> Loading SkillGraph Intelligence Engine...
      </div>
    );
  }

  const { user, evidence, skills, role_profile, gap_analysis, roadmap, history, available_assessments, mentor_feedback, taxonomy_skills } = overview;
  const completedTasks = roadmap.filter(t => t.status === 'completed').length;
  const roadmapPct = roadmap.length ? Math.round((completedTasks / roadmap.length) * 100) : 100;

  const chartData = gap_analysis.map(g => ({
    name: g.skill_name.split('&')[0].trim(),
    Verified: g.current_level,
    Required: g.required_level
  }));

  const navItems = [
    { id: 'dashboard', label: 'Skill Dashboard', icon: BarChart3 },
    { id: 'evidence', label: `Evidence Engine (${evidence.length})`, icon: GitBranch },
    { id: 'gaps', label: 'Role Match & Gaps', icon: Compass },
    { id: 'assessments', label: 'Practical Assessments', icon: Code2 },
    { id: 'roadmap', label: `Roadmap (${completedTasks}/${roadmap.length})`, icon: Layers },
    { id: 'profile', label: 'Profile & Privacy', icon: UserCog }
  ];

  return (
    <div className="min-h-screen bg-obsidian text-slate-100 flex flex-col">
      <header className="border-b border-slate-800 bg-surface/95 backdrop-blur sticky top-0 z-30 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-sky-500/15 border border-sky-500/40 flex items-center justify-center text-sky-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-white tracking-tight">SkillGraph</span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-sky-300 border border-slate-700">
                Team Kaizen
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Students list skills. We check the evidence.</p>
          </div>
        </div>

        <nav className="flex flex-wrap items-center gap-1.5">
          {navItems.map(item => {
            const Icon = item.icon;
            const active = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  active ? 'bg-sky-500 text-slate-950 font-semibold' : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <Icon className="w-3.5 h-3.5" /> {item.label}
              </button>
            );
          })}
        </nav>

        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <div className="text-xs font-medium text-white">{user.name}</div>
            <div className="text-[11px] text-sky-400">Target: {role_profile.role_name}</div>
          </div>
          <button
            onClick={handleLogout}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </header>

      {toast && (
        <div className={`fixed bottom-5 right-5 z-50 max-w-md px-4 py-3 rounded-xl text-sm shadow-2xl border ${
          toast.type === 'error' ? 'bg-rose-950/95 border-rose-500 text-rose-200' : 'bg-emerald-950/95 border-emerald-500 text-emerald-200'
        }`}>
          {toast.msg}
        </div>
      )}

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-surface border border-slate-800 rounded-2xl p-4">
            <div className="text-xs text-slate-400">Target Role Match Score</div>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">{role_profile.role_match_score}%</span>
              <span className="text-xs text-sky-400">{role_profile.role_name}</span>
            </div>
            <div className="mt-2 h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-sky-400" style={{ width: `${role_profile.role_match_score}%` }} />
            </div>
          </div>

          <div className="bg-surface border border-slate-800 rounded-2xl p-4">
            <div className="text-xs text-slate-400">Evidence Coverage (Verified)</div>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-emerald-400">{role_profile.evidence_coverage_score}%</span>
              <span className="text-xs text-slate-400">Code / Test Backed</span>
            </div>
            <div className="mt-2 h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-400" style={{ width: `${role_profile.evidence_coverage_score}%` }} />
            </div>
          </div>

          <div className="bg-surface border border-slate-800 rounded-2xl p-4">
            <div className="text-xs text-slate-400">Submitted Evidence Items</div>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">{evidence.length}</span>
              <span className="text-xs text-slate-400">Repos, Docs & Claims</span>
            </div>
            <button onClick={() => setActiveTab('evidence')} className="mt-2 text-xs text-sky-400 hover:underline">
              + Add GitHub Repo or ZIP →
            </button>
          </div>

          <div className="bg-surface border border-slate-800 rounded-2xl p-4">
            <div className="text-xs text-slate-400">Personalized Roadmap</div>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-amber-400">{roadmapPct}%</span>
              <span className="text-xs text-slate-400">{completedTasks}/{roadmap.length} Tasks Done</span>
            </div>
            <button onClick={() => setActiveTab('roadmap')} className="mt-2 text-xs text-amber-300 hover:underline">
              View Gap Closure Plan →
            </button>
          </div>
        </div>

        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <div className="grid lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 bg-surface border border-slate-800 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-base font-semibold text-white">Verified Proficiency vs. {role_profile.role_name} Benchmark</h2>
                    <p className="text-xs text-slate-400">Proficiency Scale: 0 (Not Demonstrated) to 4 (Advanced)</p>
                  </div>
                </div>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                      <XAxis dataKey="name" stroke="#94A3B8" fontSize={11} />
                      <YAxis domain={[0, 4]} ticks={[0, 1, 2, 3, 4]} stroke="#94A3B8" fontSize={11} />
                      <Tooltip contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155' }} />
                      <Legend />
                      <Bar dataKey="Verified" name="Demonstrated Level" fill="#38BDF8" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Required" name="Role Target Level" fill="#334155" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-surface border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4">
                <div>
                  <h2 className="text-base font-semibold text-white flex items-center gap-2">
                    <Award className="w-4 h-4 text-emerald-400" /> Faculty & Mentor Reviews
                  </h2>
                  {mentor_feedback.length === 0 ? (
                    <p className="mt-3 text-xs text-slate-400">No mentor reviews posted yet.</p>
                  ) : (
                    <div className="mt-3 space-y-3">
                      {mentor_feedback.map(fb => (
                        <div key={fb.id} className="p-3 rounded-xl bg-obsidian border border-slate-800 text-xs space-y-1.5">
                          <div className="flex justify-between items-center">
                            <span className="font-semibold text-emerald-300">{fb.mentor_name}</span>
                            <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 text-[10px]">{fb.endorsement_tag}</span>
                          </div>
                          <p className="text-slate-300 leading-relaxed">{fb.comment}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" /> Reassessment & Audit History
                  </h3>
                  <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                    {history.length === 0 ? (
                      <p className="text-xs text-slate-500">Submit new evidence or take an assessment to record skill progression.</p>
                    ) : (
                      history.map(h => (
                        <div key={h.id} className="text-xs p-2 rounded-lg bg-obsidian/80 border border-slate-800/80">
                          <div className="font-medium text-sky-300">{h.skill_name}: L{h.previous_level} → L{h.new_level}</div>
                          <div className="text-[11px] text-slate-400">{h.trigger_reason}</div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-surface border border-slate-800 rounded-2xl p-6">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
                <div>
                  <h2 className="text-base font-semibold text-white">Explainable Evidence-Backed Skill Profile</h2>
                  <p className="text-xs text-slate-400">Proficiency (0–4) is calculated independently from Confidence (%) and Evidence Status.</p>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                {skills.map(sk => {
                  const badge = STATUS_BADGES[sk.evidence_status] || STATUS_BADGES.missing;
                  return (
                    <div key={sk.skill_name} className="bg-obsidian border border-slate-800 rounded-xl p-4 space-y-2.5">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="font-semibold text-white text-sm">{sk.skill_name}</div>
                          <div className="text-[11px] text-slate-400">{sk.category}</div>
                        </div>
                        <span className={`text-[11px] px-2.5 py-0.5 rounded-full border ${badge.cls}`}>
                          {badge.label}
                        </span>
                      </div>

                      <div className="flex items-center justify-between text-xs pt-1">
                        <span className="font-medium text-sky-300">
                          Proficiency: {LEVEL_LABELS[sk.proficiency_level]}
                        </span>
                        <span className="text-slate-300">
                          Confidence: <strong>{sk.confidence_score}%</strong>
                        </span>
                      </div>

                      <p className="text-xs text-slate-400 leading-relaxed">{sk.explanation}</p>

                      {sk.supporting_evidence?.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {sk.supporting_evidence.map((evTitle, idx) => (
                            <span key={idx} className="text-[11px] px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                              {evTitle}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'evidence' && (
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="space-y-6">
              <form onSubmit={submitGitHub} className="bg-surface border border-slate-800 rounded-2xl p-5 space-y-3">
                <div className="flex items-center gap-2 text-white font-semibold text-sm">
                  <GitBranch className="w-4 h-4 text-sky-400" /> Analyze Public GitHub Repository
                </div>
                <p className="text-xs text-slate-400">
                  Inspects languages, file tree, dependencies, and README in read-only mode. Try any public repo (e.g. <code className="text-sky-300">https://github.com/tiangolo/fastapi</code>).
                </p>
                <input
                  type="url"
                  required
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/username/repository"
                  className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                />
                <label className="flex items-start gap-2 text-xs text-slate-400 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={repoConsent}
                    onChange={(e) => setRepoConsent(e.target.checked)}
                    className="mt-0.5"
                  />
                  <span>I grant SkillGraph read-only consent to inspect this public repository.</span>
                </label>
                <button
                  type="submit"
                  disabled={submittingEvidence}
                  className="w-full py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-xs"
                >
                  {submittingEvidence ? 'Inspecting Repository...' : 'Run Evidence Extraction'}
                </button>
              </form>

              <div className="bg-surface border border-slate-800 rounded-2xl p-5 space-y-3">
                <div className="flex items-center gap-2 text-white font-semibold text-sm">
                  <UploadCloud className="w-4 h-4 text-emerald-400" /> Upload Project ZIP or PDF Docs
                </div>
                <p className="text-xs text-slate-400">
                  Upload a project <code className="text-slate-300">.zip</code> archive (protected against Zip-Slip traversal, max 15MB) or architecture <code className="text-slate-300">.pdf</code> report.
                </p>
                <label className="block border-2 border-dashed border-slate-700 hover:border-sky-500 rounded-xl p-4 text-center cursor-pointer transition">
                  <span className="text-xs text-sky-300 font-medium">
                    {submittingEvidence ? 'Analyzing file...' : 'Click to choose .ZIP or .PDF file'}
                  </span>
                  <input type="file" accept=".zip,.pdf" onChange={submitFileUpload} disabled={submittingEvidence} className="hidden" />
                </label>
              </div>

              <form onSubmit={submitClaim} className="bg-surface border border-slate-800 rounded-2xl p-5 space-y-3">
                <div className="flex items-center gap-2 text-white font-semibold text-sm">
                  <PlusCircle className="w-4 h-4 text-amber-400" /> Add Self-Declared Skill
                </div>
                <p className="text-xs text-slate-400">
                  Claimed skills are tracked separately and capped at Level 1 until backed by code or assessment proof.
                </p>
                <select
                  value={claimSkill}
                  onChange={(e) => setClaimSkill(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                >
                  {taxonomy_skills.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                <input
                  value={claimNotes}
                  onChange={(e) => setClaimNotes(e.target.value)}
                  placeholder="Optional context (e.g., Used in coursework)"
                  className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-xs"
                />
                <button
                  type="submit"
                  disabled={submittingEvidence}
                  className="w-full py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold text-xs"
                >
                  Declare Skill
                </button>
              </form>
            </div>

            <div className="lg:col-span-2 bg-surface border border-slate-800 rounded-2xl p-6 space-y-4">
              <h2 className="text-base font-semibold text-white">Submitted Evidence & Extracted Technical Signals</h2>
              <div className="space-y-3">
                {evidence.map(ev => (
                  <div key={ev.id} className="bg-obsidian border border-slate-800 rounded-xl p-4 space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-sky-300 mr-2">
                          {ev.source_type}
                        </span>
                        <span className="font-semibold text-sm text-white">{ev.title}</span>
                      </div>
                      <button
                        onClick={() => deleteEvidence(ev.id)}
                        className="text-slate-500 hover:text-rose-400 p-1"
                        title="Remove evidence and recalculate"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="text-xs text-slate-400">{ev.summary}</p>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {Object.entries(ev.detected_skills || {}).map(([skName, info]) => (
                        <span key={skName} className="text-[11px] px-2 py-0.5 rounded bg-sky-500/10 text-sky-300 border border-sky-500/25">
                          {skName} ({info.signal_count} signals)
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'gaps' && (
          <div className="bg-surface border border-slate-800 rounded-2xl p-6 space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-white">Career Role Intelligence: {role_profile.role_name}</h2>
                <p className="text-xs text-slate-400">{role_profile.description}</p>
              </div>
              <div className="flex gap-4 text-xs">
                <div className="px-3 py-2 rounded-xl bg-obsidian border border-slate-800">
                  Role Match: <strong className="text-sky-400">{role_profile.role_match_score}%</strong>
                </div>
                <div className="px-3 py-2 rounded-xl bg-obsidian border border-slate-800">
                  Evidence Coverage: <strong className="text-emerald-400">{role_profile.evidence_coverage_score}%</strong>
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="py-3 px-3">Required Skill</th>
                    <th className="py-3 px-3">Weight</th>
                    <th className="py-3 px-3">Target</th>
                    <th className="py-3 px-3">Current</th>
                    <th className="py-3 px-3">Gap Status</th>
                    <th className="py-3 px-3">Evidence Basis & Explanation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80">
                  {gap_analysis.map(g => (
                    <tr key={g.skill_name} className="hover:bg-slate-900/40">
                      <td className="py-3.5 px-3 font-semibold text-white">{g.skill_name}</td>
                      <td className="py-3.5 px-3 text-slate-300">{g.importance_pct}% ({g.criticality})</td>
                      <td className="py-3.5 px-3 text-slate-300">Level {g.required_level}</td>
                      <td className="py-3.5 px-3 font-semibold text-sky-300">Level {g.current_level}</td>
                      <td className="py-3.5 px-3">
                        <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-medium ${
                          g.classification === 'Met & Verified'
                            ? 'bg-emerald-500/15 text-emerald-300'
                            : g.classification === 'Partially Developed'
                            ? 'bg-amber-500/15 text-amber-300'
                            : 'bg-rose-500/15 text-rose-300'
                        }`}>
                          {g.classification} {g.gap_delta > 0 ? `(-${g.gap_delta} lvl)` : ''}
                        </span>
                      </td>
                      <td className="py-3.5 px-3 text-slate-400 max-w-md">{g.explanation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'assessments' && (
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="space-y-3">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">Role-Specific Practical Challenges</h2>
              {available_assessments.map(a => (
                <button
                  key={a.id}
                  onClick={() => {
                    setSelectedAssessment(a);
                    setAssessmentCode(a.starter_code);
                    setAssessmentResult(null);
                  }}
                  className={`w-full text-left p-4 rounded-xl border transition ${
                    selectedAssessment?.id === a.id
                      ? 'bg-sky-500/15 border-sky-500 text-white'
                      : 'bg-surface border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <div className="text-xs text-sky-400 font-medium">{a.skill_name}</div>
                  <div className="font-semibold text-sm mt-0.5">{a.title}</div>
                  <div className="text-[11px] text-slate-400 mt-1">{a.difficulty}</div>
                </button>
              ))}
            </div>

            {selectedAssessment && (
              <div className="lg:col-span-2 bg-surface border border-slate-800 rounded-2xl p-6 space-y-4">
                <div>
                  <span className="text-xs px-2.5 py-0.5 rounded bg-sky-500/15 text-sky-300">{selectedAssessment.skill_name}</span>
                  <h3 className="text-lg font-semibold text-white mt-2">{selectedAssessment.title}</h3>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">{selectedAssessment.prompt}</p>
                </div>

                <div className="bg-obsidian border border-slate-800 rounded-xl p-3">
                  <div className="text-[11px] font-semibold text-slate-400 mb-1.5">Evaluation Rubric Criteria:</div>
                  <ul className="space-y-1 text-xs text-slate-300 list-disc list-inside">
                    {selectedAssessment.rubric_criteria.map((c, idx) => <li key={idx}>{c}</li>)}
                  </ul>
                </div>

                <div>
                  <label className="block text-xs text-slate-400 mb-1">Your Solution (Code / SQL / Dockerfile)</label>
                  <textarea
                    rows={8}
                    value={assessmentCode}
                    onChange={(e) => setAssessmentCode(e.target.value)}
                    className="w-full font-mono text-xs p-3 rounded-xl bg-obsidian border border-slate-700 text-emerald-300 focus:border-sky-500 outline-none"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <button
                    onClick={submitAssessment}
                    disabled={submittingEvidence}
                    className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs"
                  >
                    {submittingEvidence ? 'Evaluating Against Rubric...' : 'Submit & Validate Skill'}
                  </button>
                  <span className="text-xs text-slate-400">Passing score (≥65) upgrades skill to Assessment-Validated</span>
                </div>

                {assessmentResult && (
                  <div className={`p-4 rounded-xl border text-xs ${
                    assessmentResult.passed ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-200' : 'bg-amber-500/10 border-amber-500/40 text-amber-200'
                  }`}>
                    {assessmentResult.feedback}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'roadmap' && (
          <div className="bg-surface border border-slate-800 rounded-2xl p-6 space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h2 className="text-lg font-semibold text-white">Personalized Gap-Closure Roadmap</h2>
                <p className="text-xs text-slate-400">Dynamically prioritized from your verified skill gaps. Click any task badge to update progress.</p>
              </div>
              <span className="text-xs px-3 py-1.5 rounded-full bg-sky-500/15 text-sky-300 border border-sky-500/30">
                Completion: {roadmapPct}% ({completedTasks}/{roadmap.length})
              </span>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {roadmap.map(task => (
                <div key={task.id} className="bg-obsidian border border-slate-800 rounded-xl p-5 flex flex-col justify-between space-y-3">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className={`text-[11px] px-2 py-0.5 rounded font-semibold ${
                        task.priority === 'Critical' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'
                      }`}>
                        {task.priority} · {task.skill_name}
                      </span>
                      <button
                        onClick={() => toggleTaskStatus(task)}
                        className={`text-[11px] px-2.5 py-1 rounded-full font-semibold capitalize transition ${
                          task.status === 'completed'
                            ? 'bg-emerald-500 text-slate-950'
                            : task.status === 'in_progress'
                            ? 'bg-sky-500 text-slate-950'
                            : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                        }`}
                      >
                        {task.status.replace('_', ' ')} ↻
                      </button>
                    </div>
                    <h3 className="font-semibold text-sm text-white">{task.title}</h3>
                    <p className="text-xs text-slate-400 leading-relaxed">{task.project_activity}</p>
                  </div>

                  <a
                    href={task.resource_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs text-sky-400 hover:underline pt-1"
                  >
                    <ExternalLink className="w-3.5 h-3.5" /> {task.resource_label}
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'profile' && profileForm && (
          <form onSubmit={saveProfile} className="max-w-2xl bg-surface border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-semibold text-white">Student Profile, Target Role & Consent Controls</h2>
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Full Name</label>
                <input
                  value={profileForm.name}
                  onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Target Career Role</label>
                <select
                  value={profileForm.target_role}
                  onChange={(e) => setProfileForm({ ...profileForm, target_role: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                >
                  {role_profile.available_roles.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Degree / Education</label>
                <input
                  value={profileForm.education}
                  onChange={(e) => setProfileForm({ ...profileForm, education: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Institution</label>
                <input
                  value={profileForm.institution}
                  onChange={(e) => setProfileForm({ ...profileForm, institution: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-obsidian border border-slate-700 text-sm"
                />
              </div>
            </div>

            <label className="flex items-start gap-2.5 p-3 rounded-xl bg-obsidian border border-slate-800 text-xs text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={profileForm.faculty_consent}
                onChange={(e) => setProfileForm({ ...profileForm, faculty_consent: e.target.checked })}
                className="mt-0.5"
              />
              <span>
                <strong>Faculty & Placement Sharing Permission:</strong> Allow authorized institution mentors to inspect my verified skill profile and submit evidence feedback.
              </span>
            </label>

            <button type="submit" className="px-5 py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-xs">
              Save Preferences & Recalculate Role Match
            </button>
          </form>
        )}
      </main>
    </div>
  );
}
