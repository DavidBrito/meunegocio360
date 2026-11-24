import { useMutation } from '@tanstack/react-query'
import * as authApi from '../api/authApi.js'
import { useAuth } from './useAuth.js'

export function useLogin() {
  const { entrar } = useAuth()
  return useMutation({ mutationFn: authApi.login, onSuccess: entrar })
}
