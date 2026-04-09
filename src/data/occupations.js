export const OCCUPATIONS = [
  // ── Tech ──────────────────────────────────────────────────────────────────
  { code: '15-1252', label: 'Software Developer / Engineer',           category: 'Tech' },
  { code: '15-2051', label: 'Data Scientist',                          category: 'Tech' },
  { code: '15-1211', label: 'Computer Systems Analyst',                category: 'Tech' },
  { code: '15-1244', label: 'Network & Systems Administrator',         category: 'Tech' },
  { code: '15-1255', label: 'Web Developer',                           category: 'Tech' },
  { code: '15-1232', label: 'IT Support Specialist',                   category: 'Tech' },
  { code: '15-2031', label: 'Operations Research Analyst',             category: 'Tech' },
  // ── Management & Business ─────────────────────────────────────────────────
  { code: '11-1021', label: 'General & Operations Manager',            category: 'Business' },
  { code: '11-3031', label: 'Financial Manager',                       category: 'Business' },
  { code: '11-9041', label: 'Engineering Manager',                     category: 'Business' },
  { code: '13-1111', label: 'Management Consultant',                   category: 'Business' },
  { code: '13-1071', label: 'Human Resources Specialist',              category: 'Business' },
  { code: '13-1081', label: 'Logistician',                             category: 'Business' },
  { code: '13-2011', label: 'Accountant / Auditor',                    category: 'Business' },
  { code: '13-1161', label: 'Market Research Analyst',                 category: 'Business' },
  { code: '43-3031', label: 'Bookkeeping / Accounting Clerk',          category: 'Business' },
  { code: '43-6014', label: 'Administrative Assistant',                category: 'Business' },
  // ── Legal ─────────────────────────────────────────────────────────────────
  { code: '23-1011', label: 'Lawyer / Attorney',                       category: 'Legal' },
  // ── Healthcare ────────────────────────────────────────────────────────────
  { code: '29-1141', label: 'Registered Nurse',                        category: 'Healthcare' },
  { code: '29-1071', label: 'Physician Assistant',                     category: 'Healthcare' },
  { code: '29-2061', label: 'Licensed Practical Nurse (LPN)',          category: 'Healthcare' },
  { code: '29-1051', label: 'Pharmacist',                              category: 'Healthcare' },
  { code: '29-2034', label: 'Radiologic Technologist',                 category: 'Healthcare' },
  { code: '21-1014', label: 'Mental Health Counselor',                 category: 'Healthcare' },
  // ── Engineering ───────────────────────────────────────────────────────────
  { code: '17-2141', label: 'Mechanical Engineer',                     category: 'Engineering' },
  { code: '17-2051', label: 'Civil Engineer',                          category: 'Engineering' },
  { code: '17-2071', label: 'Electrical Engineer',                     category: 'Engineering' },
  { code: '17-2112', label: 'Industrial Engineer',                     category: 'Engineering' },
  // ── Education ─────────────────────────────────────────────────────────────
  { code: '25-2021', label: 'Elementary School Teacher',               category: 'Education' },
  { code: '25-1099', label: 'College Professor',                       category: 'Education' },
  // ── Trades & Public Safety ────────────────────────────────────────────────
  { code: '47-2111', label: 'Electrician',                             category: 'Trades' },
  { code: '47-2152', label: 'Plumber / Pipefitter',                    category: 'Trades' },
  { code: '33-3051', label: 'Police Officer',                          category: 'Trades' },
  // ── Creative & Service ────────────────────────────────────────────────────
  { code: '27-1024', label: 'Graphic Designer',                        category: 'Creative' },
  { code: '35-1012', label: 'Food Service Manager',                    category: 'Service' },
  { code: '41-2031', label: 'Retail Sales Worker',                     category: 'Service' },
]

export const OCCUPATION_CATEGORIES = [...new Set(OCCUPATIONS.map(o => o.category))]

export const DEFAULT_OCCUPATION = '15-1252'

