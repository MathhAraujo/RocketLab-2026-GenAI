import { Routes, Route } from 'react-router-dom'
import CatalogPage from './pages/CatalogPage'
import ProductDetailPage from './pages/ProductDetailPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<CatalogPage />} />
      <Route path="/produtos/:id" element={<ProductDetailPage />} />
    </Routes>
  )
}
