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
    id: 'openai/gpt-5.2-chat',
    name: 'GPT-5.2 Chat',
    provider: 'OpenAI',
    category: 'pro',
    description: 'Новейшая разговорная модель с улучшенным пониманием контекста',
    contextWindow: 128000,
    specialties: ['Диалог', 'Анализ', 'Генерация кода']
  },
  {
    id: 'openai/gpt-5.2-pro',
    name: 'GPT-5.2 Pro',
    provider: 'OpenAI',
    category: 'pro',
    description: 'Профессиональная версия для сложных задач',
    contextWindow: 128000,
    specialties: ['Архитектура', 'Рефакторинг', 'Оптимизация']
  },
  {
    id: 'openai/gpt-5.2',
    name: 'GPT-5.2',
    provider: 'OpenAI',
    category: 'pro',
    description: 'Базовая модель GPT-5.2 с балансом скорости и качества',
    contextWindow: 128000,
    specialties: ['Универсальные задачи']
  },
  {
    id: 'anthropic/claude-opus-4.5',
    name: 'Claude Opus 4.5',
    provider: 'Anthropic',
    category: 'pro',
    description: 'Мощная модель для сложного анализа и длинных документов',
    contextWindow: 200000,
    specialties: ['Анализ кода', 'Документация', 'Безопасность']
  },
  {
    id: 'openai/gpt-5.1',
    name: 'GPT-5.1',
    provider: 'OpenAI',
    category: 'pro',
    description: 'Предыдущее поколение с проверенной стабильностью',
    contextWindow: 100000,
    specialties: ['Стабильность', 'Надежность']
  },
  {
    id: 'openai/gpt-5.1-chat',
    name: 'GPT-5.1 Chat',
    provider: 'OpenAI',
    category: 'standard',
    description: 'Разговорная версия GPT-5.1',
    contextWindow: 100000,
    specialties: ['Диалог', 'Консультации']
  },
  {
    id: 'openai/o3-deep-research',
    name: 'O3 Deep Research',
    provider: 'OpenAI',
    category: 'specialized',
    description: 'Специализированная модель для глубокого исследования кода',
    contextWindow: 150000,
    specialties: ['Исследование', 'Анализ паттернов', 'Оптимизация']
  },
  {
    id: 'openai/gpt-5-pro',
    name: 'GPT-5 Pro',
    provider: 'OpenAI',
    category: 'pro',
    description: 'Профессиональная версия GPT-5',
    contextWindow: 120000,
    specialties: ['Enterprise задачи']
  },
  {
    id: 'anthropic/claude-sonnet-4.5',
    name: 'Claude Sonnet 4.5',
    provider: 'Anthropic',
    category: 'standard',
    description: 'Быстрая модель с хорошим балансом качества',
    contextWindow: 150000,
    specialties: ['Скорость', 'Эффективность']
  },
  {
    id: 'x-ai/grok-code-fast-1',
    name: 'Grok Code Fast',
    provider: 'xAI',
    category: 'specialized',
    description: 'Быстрая модель для кодинга от xAI',
    contextWindow: 80000,
    specialties: ['Быстрая генерация', 'Прототипирование']
  },
  {
    id: 'openai/gpt-5.1-codex',
    name: 'GPT-5.1 Codex',
    provider: 'OpenAI',
    category: 'specialized',
    description: 'Специализированная модель для программирования',
    contextWindow: 100000,
    specialties: ['Генерация кода', 'Отладка', 'Рефакторинг']
  },
  {
    id: 'openai/gpt-5.1-codex-max',
    name: 'GPT-5.1 Codex Max',
    provider: 'OpenAI',
    category: 'specialized',
    description: 'Расширенная версия Codex с большим контекстом',
    contextWindow: 150000,
    specialties: ['Большие проекты', 'Архитектура']
  },
  {
    id: 'openai/gpt-5-codex',
    name: 'GPT-5 Codex',
    provider: 'OpenAI',
    category: 'specialized',
    description: 'Новейшая версия кодовой модели',
    contextWindow: 120000,
    specialties: ['Современные фреймворки', 'Best practices']
  },
  {
    id: 'qwen/qwen3-coder',
    name: 'Qwen3 Coder',
    provider: 'Qwen',
    category: 'standard',
    description: 'Открытая модель для программирования',
    contextWindow: 32000,
    specialties: ['Python', 'JavaScript', 'TypeScript']
  },
  {
    id: 'mistralai/codestral-2508',
    name: 'Codestral 2508',
    provider: 'Mistral AI',
    category: 'standard',
    description: 'Специализированная модель от Mistral',
    contextWindow: 32000,
    specialties: ['Европейские языки', 'Многоязычность']
  },
  {
    id: 'qwen/qwen3-coder-plus',
    name: 'Qwen3 Coder Plus',
    provider: 'Qwen',
    category: 'standard',
    description: 'Улучшенная версия Qwen3 Coder',
    contextWindow: 64000,
    specialties: ['Расширенный контекст']
  },
  {
    id: 'kwaipilot/kat-coder-pro',
    name: 'KAT Coder Pro',
    provider: 'KwaiPilot',
    category: 'specialized',
    description: 'Профессиональная модель для кодирования',
    contextWindow: 40000,
    specialties: ['Азиатские языки', 'Локализация']
  },
  {
    id: 'arcee-ai/coder-large',
    name: 'Arcee Coder Large',
    provider: 'Arcee AI',
    category: 'standard',
    description: 'Крупная модель для комплексных задач',
    contextWindow: 50000,
    specialties: ['Сложная логика']
  },
  {
    id: 'agentica-org/deepcoder-14b-preview',
    name: 'DeepCoder 14B',
    provider: 'Agentica',
    category: 'specialized',
    description: 'Экспериментальная модель для deep coding',
    contextWindow: 32000,
    specialties: ['Алгоритмы', 'Оптимизация']
  },
  {
    id: 'google/palm-2-codechat-bison-32k',
    name: 'PaLM 2 CodeChat 32K',
    provider: 'Google',
    category: 'standard',
    description: 'Модель Google для кодирования с большим контекстом',
    contextWindow: 32000,
    specialties: ['Google Cloud', 'Android']
  },
  {
    id: 'google/palm-2-codechat-bison',
    name: 'PaLM 2 CodeChat',
    provider: 'Google',
    category: 'standard',
    description: 'Базовая модель Google для программирования',
    contextWindow: 8000,
    specialties: ['Быстрые ответы']
  },
  {
    id: 'kwaipilot/kat-coder-pro:free',
    name: 'KAT Coder Pro Free',
    provider: 'KwaiPilot',
    category: 'free',
    description: 'Бесплатная версия KAT Coder Pro',
    contextWindow: 20000,
    specialties: ['Базовые задачи']
  },
  {
    id: 'qwen/qwen3-coder:free',
    name: 'Qwen3 Coder Free',
    provider: 'Qwen',
    category: 'free',
    description: 'Бесплатная версия Qwen3 Coder',
    contextWindow: 16000,
    specialties: ['Обучение', 'Эксперименты']
  },
  {
    id: 'qwen/qwen3-coder:exacto',
    name: 'Qwen3 Coder Exacto',
    provider: 'Qwen',
    category: 'specialized',
    description: 'Точная версия для строгого следования спецификациям',
    contextWindow: 32000,
    specialties: ['Точность', 'Спецификации']
  }
];

export const getModelsByCategory = (category: AIModel['category']) => 
  AI_MODELS.filter(m => m.category === category);

export const getModelById = (id: string) => 
  AI_MODELS.find(m => m.id === id);
