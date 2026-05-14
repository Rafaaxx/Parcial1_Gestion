/**
 * AdminDashboard — Admin panel home with metrics and charts
 */

import React, { useState } from 'react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { useResumen, useVentas, usePedidosPorEstado, useProductosTop } from '@/features/admin'

// Colores para el gráfico de donut
const COLORS = ['#10B981', '#F59E0B', '#3B82F6', '#EF4444', '#8B5CF6', '#EC4899']

export const AdminDashboard: React.FC = () => {
  const [granularidad, setGranularidad] = useState<'dia' | 'semana' | 'mes'>('dia')

  // Obtener datos
  const { data: resumen, isLoading: resumenLoading } = useResumen()
  const { data: ventas, isLoading: ventasLoading } = useVentas(granularidad)
  const { data: pedidosEstado, isLoading: pedidosLoading } = usePedidosPorEstado()
  const { data: productosTop, isLoading: productosLoading } = useProductosTop(10)

  // Formatear moneda
  const formatCurrency = (value: string) => {
    const num = parseFloat(value)
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 0,
    }).format(num)
  }

  // Formatear número
  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('es-AR').format(value)
  }

  if (resumenLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  const stats = [
    {
      label: 'Ingresos Totales',
      value: formatCurrency(resumen?.total_ventas || '0'),
      icon: '💰',
      color: 'bg-green-500',
    },
    {
      label: 'Pedidos',
      value: formatNumber(resumen?.cantidad_pedidos || 0),
      icon: '📦',
      color: 'bg-blue-500',
    },
    {
      label: 'Usuarios Registrados',
      value: formatNumber(resumen?.usuarios_registrados || 0),
      icon: '👥',
      color: 'bg-purple-500',
    },
    {
      label: 'Productos Vendidos',
      value: formatNumber(resumen?.productos_mas_vendidos?.reduce((acc, p) => acc + p.cantidad_total, 0) || 0),
      icon: '🏆',
      color: 'bg-orange-500',
    },
  ]

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
        Dashboard
      </h1>

      {/* Stats Cards - 4 columnas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <div
            key={index}
            className="card-base p-4 flex items-center gap-4"
          >
            <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center text-2xl`}>
              {stat.icon}
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Gráficos - 2 columnas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de Ventas */}
        <div className="card-base p-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
              Ventas
            </h2>
            <select
              value={granularidad}
              onChange={(e) => setGranularidad(e.target.value as 'dia' | 'semana' | 'mes')}
              className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
            >
              <option value="dia">Día</option>
              <option value="semana">Semana</option>
              <option value="mes">Mes</option>
            </select>
          </div>
          {ventasLoading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={ventas || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="periodo"
                  stroke="#9CA3AF"
                  fontSize={12}
                />
                <YAxis
                  stroke="#9CA3AF"
                  fontSize={12}
                  tickFormatter={(value) => `$${value / 1000}k`}
                />
                <Tooltip
                  formatter={(value: number) => [formatCurrency(String(value)), 'Ventas']}
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#F9FAFB',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="monto_total"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  dot={false}
                  name="Ventas"
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Gráfico Donut de Pedidos por Estado */}
        <div className="card-base p-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
            Pedidos por Estado
          </h2>
          {pedidosLoading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pedidosEstado || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="cantidad"
                  nameKey="estado"
                  label={({ estado, porcentaje }) => `${estado} ${porcentaje}%`}
                  labelLine={false}
                >
                  {(pedidosEstado || []).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number, name: string) => [value, name]}
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#F9FAFB',
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Gráfico de Productos Más Vendidos */}
      <div className="card-base p-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
          Productos Más Vendidos
        </h2>
        {productosLoading ? (
          <div className="h-64 flex items-center justify-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={productosTop?.slice(0, 5) || []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" stroke="#9CA3AF" fontSize={12} />
              <YAxis
                type="category"
                dataKey="nombre"
                stroke="#9CA3AF"
                fontSize={12}
                width={120}
                tick={{ fontSize: 11 }}
              />
              <Tooltip
                formatter={(value: number, name: string) => [value, name === 'cantidad_total' ? 'Cantidad' : name]}
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#F9FAFB',
                }}
              />
              <Bar dataKey="cantidad_total" fill="#3B82F6" radius={[0, 4, 4, 0]} name="Cantidad" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}

export default AdminDashboard
