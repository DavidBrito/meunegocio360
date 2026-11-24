import { useEffect, useState } from 'react'

/** Contagem regressiva em segundos (usada no bloqueio 429 do login). */
export function useCountdown() {
  const [fim, setFim] = useState(null)
  const [agora, setAgora] = useState(0)

  useEffect(() => {
    if (fim === null) return undefined
    const id = setInterval(() => {
      const t = Date.now()
      setAgora(t)
      if (t >= fim) setFim(null)
    }, 1000)
    return () => clearInterval(id)
  }, [fim])

  const restante =
    fim === null ? 0 : Math.max(0, Math.ceil((fim - agora) / 1000))

  function iniciar(segundos) {
    const t = Date.now()
    setAgora(t)
    setFim(t + segundos * 1000)
  }

  return { restante, iniciar }
}
