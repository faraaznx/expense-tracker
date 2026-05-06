import '@testing-library/jest-dom'

// Node.js 25 ships a native (non-functional) localStorage that shadows jsdom's.
// If localStorage.clear is not a function, replace with jsdom's working Storage via vi.stubGlobal.
// This runs in setup (before tests) so the jsdom window is already initialized.
if (typeof globalThis.localStorage?.clear !== 'function' && typeof globalThis.jsdom !== 'undefined') {
  const jsdomLocalStorage = globalThis.jsdom.window.localStorage
  const jsdomSessionStorage = globalThis.jsdom.window.sessionStorage
  Object.defineProperty(globalThis, 'localStorage', {
    value: jsdomLocalStorage,
    writable: true,
    configurable: true,
  })
  Object.defineProperty(globalThis, 'sessionStorage', {
    value: jsdomSessionStorage,
    writable: true,
    configurable: true,
  })
}
