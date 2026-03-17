import { createContext, useContext, useReducer } from 'react'
import { OCCUPATIONS, DEFAULT_OCCUPATION } from '../data/occupations.js'

const defaultOccupation = OCCUPATIONS.find(o => o.code === DEFAULT_OCCUPATION)

const initialState = {
  occupation: defaultOccupation,
  salary: null,
  usingCustomSalary: false,
  pinnedCities: [],
  compareOpen: false,
}

function reducer(state, action) {
  switch (action.type) {
    case 'SET_OCCUPATION':
      return { ...state, occupation: action.payload, salary: null, usingCustomSalary: false }
    case 'SET_SALARY':
      return { ...state, salary: action.payload, usingCustomSalary: true }
    case 'CLEAR_SALARY':
      return { ...state, salary: null, usingCustomSalary: false }
    case 'PIN_CITY':
      if (state.pinnedCities.includes(action.payload) || state.pinnedCities.length >= 3) return state
      return { ...state, pinnedCities: [...state.pinnedCities, action.payload] }
    case 'UNPIN_CITY':
      return { ...state, pinnedCities: state.pinnedCities.filter(id => id !== action.payload) }
    case 'TOGGLE_COMPARE':
      return { ...state, compareOpen: !state.compareOpen }
    default:
      return state
  }
}

const UserProfileContext = createContext(null)

export function UserProfileProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState)
  return (
    <UserProfileContext.Provider value={[state, dispatch]}>
      {children}
    </UserProfileContext.Provider>
  )
}

export function useUserProfile() {
  const ctx = useContext(UserProfileContext)
  if (!ctx) throw new Error('useUserProfile must be used inside UserProfileProvider')
  return ctx
}

export function getCitySalary(state, city) {
  if (state.usingCustomSalary && state.salary) return state.salary
  return city?.salaries?.[state.occupation?.code] || 75000
}
