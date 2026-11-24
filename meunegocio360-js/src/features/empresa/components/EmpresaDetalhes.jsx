import { mascaraCnpj, mascaraTelefone } from '../../../shared/lib/documentos.js'
import { FUSOS_HORARIOS } from '../schemas.js'

const rotuloFuso = (valor) =>
  FUSOS_HORARIOS.find((fuso) => fuso.valor === valor)?.rotulo ?? valor

/** Dados da empresa em modo leitura (todos os perfis). */
export default function EmpresaDetalhes({ empresa }) {
  const itens = [
    ['Razão social', empresa.razaoSocial],
    ['Nome fantasia', empresa.nomeFantasia],
    ['CNPJ', mascaraCnpj(empresa.cnpj)],
    ['E-mail', empresa.email],
    ['Telefone', empresa.telefone ? mascaraTelefone(empresa.telefone) : null],
    ['Fuso horário', rotuloFuso(empresa.fusoHorario)],
    ['Moeda', 'BRL — Real brasileiro'],
    ['Situação', empresa.ativa ? 'Ativa' : 'Inativa'],
  ]
  return (
    <dl className="row mb-0">
      {itens.map(([rotulo, valor]) => (
        <div key={rotulo} className="row mb-2">
          <dt className="col-sm-4">{rotulo}</dt>
          <dd className="col-sm-8 mb-0">
            {valor || <span className="text-body-secondary">—</span>}
          </dd>
        </div>
      ))}
    </dl>
  )
}
