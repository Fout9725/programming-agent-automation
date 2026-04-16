export interface AIModel {
  id: string;
  name: string;
  provider: string;
  category: 'pro' | 'standard' | 'specialized' | 'free';
  description: string;
  contextWindow?: number;
  specialties?: string[];
}

export const AI_MODELS: AIModel[] = [
  {
    id: 'deepseek/deepseek-v3.2-speciale-alt',
    name: 'DeepSeek V3.2 Speciale',
    provider: 'DeepSeek',
    category: 'pro',
    description: 'Самая мощная модель DeepSeek для архитектуры и сложного анализа',
    contextWindow: 128000,
    specialties: ['Архитектура', 'Планирование', 'Сложные задачи']
  },
  {
    id: 'deepseek/deepseek-r1-alt-0528',
    name: 'DeepSeek R1 Reasoning',
    provider: 'DeepSeek',
    category: 'pro',
    description: 'Модель с цепочкой рассуждений для точного кода',
    contextWindow: 128000,
    specialties: ['Рассуждения', 'Алгоритмы', 'Отладка']
  },
  {
    id: 'deepseek/deepseek-v3.2-exp-alt',
    name: 'DeepSeek V3.2 Experimental',
    provider: 'DeepSeek',
    category: 'pro',
    description: 'Экспериментальная модель с расширенными возможностями',
    contextWindow: 128000,
    specialties: ['Backend', 'API', 'Серверный код']
  },
  {
    id: 'deepseek/deepseek-chat-3.1-alt-fast',
    name: 'DeepSeek Chat 3.1 Fast',
    provider: 'DeepSeek',
    category: 'standard',
    description: 'Быстрая модель для генерации кода и SQL',
    contextWindow: 64000,
    specialties: ['Скорость', 'SQL', 'Быстрые задачи']
  },
  {
    id: 'qwen/qwen3.5-397b-a17b',
    name: 'Qwen 3.5 397B',
    provider: 'Qwen',
    category: 'pro',
    description: 'Крупнейшая модель Qwen с 397B параметров',
    contextWindow: 128000,
    specialties: ['Сложная архитектура', 'Полные проекты']
  },
  {
    id: 'qwen/qwen3.5-plus-2026-02-15',
    name: 'Qwen 3.5 Plus',
    provider: 'Qwen',
    category: 'standard',
    description: 'Оптимальная модель Qwen для повседневных задач',
    contextWindow: 64000,
    specialties: ['Баланс', 'Универсальность']
  },
  {
    id: 'qwen/qwen3.5-plus-2026-02-15-1m',
    name: 'Qwen 3.5 Plus 1M',
    provider: 'Qwen',
    category: 'specialized',
    description: 'Версия с контекстом 1M токенов для больших проектов',
    contextWindow: 1000000,
    specialties: ['Большие кодовые базы', 'Рефакторинг']
  },
  {
    id: 'qwen/qwen3-coder-next',
    name: 'Qwen3 Coder Next',
    provider: 'Qwen',
    category: 'specialized',
    description: 'Лучшая модель Qwen для генерации кода',
    contextWindow: 64000,
    specialties: ['React', 'TypeScript', 'Frontend']
  },
  {
    id: 'qwen/qwen3-235b-a22b-07-25-thinking',
    name: 'Qwen3 235B Thinking',
    provider: 'Qwen',
    category: 'pro',
    description: 'Модель с глубоким мышлением для сложных задач',
    contextWindow: 128000,
    specialties: ['Анализ', 'Рассуждения', 'Планирование']
  }
];

export const getModelsByCategory = (category: AIModel['category']) => 
  AI_MODELS.filter(m => m.category === category);

export const getModelById = (id: string) => 
  AI_MODELS.find(m => m.id === id);
