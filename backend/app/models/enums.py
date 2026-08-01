"""Enums compartilhados entre os modelos do banco de dados."""
import enum


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    USER = "USER"


class RequestPriority(str, enum.Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class RequestStatus(str, enum.Enum):
    ABERTA = "ABERTA"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    AGUARDANDO = "AGUARDANDO"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"


class RequestCategory(str, enum.Enum):
    TI = "TI"
    MANUTENCAO = "MANUTENCAO"
    RH = "RH"
    COMPRAS = "COMPRAS"
    ADMINISTRATIVO = "ADMINISTRATIVO"
    OUTROS = "OUTROS"


class HistoryAction(str, enum.Enum):
    CRIACAO = "CRIACAO"
    ALTERACAO_STATUS = "ALTERACAO_STATUS"
    ALTERACAO_PRIORIDADE = "ALTERACAO_PRIORIDADE"
    MUDANCA_RESPONSAVEL = "MUDANCA_RESPONSAVEL"
    EDICAO_DADOS = "EDICAO_DADOS"
    CONCLUSAO = "CONCLUSAO"
    CANCELAMENTO = "CANCELAMENTO"
    EXCLUSAO = "EXCLUSAO"
    COMENTARIO_ADICIONADO = "COMENTARIO_ADICIONADO"
    ANEXO_ADICIONADO = "ANEXO_ADICIONADO"
