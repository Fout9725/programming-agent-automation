# OpenRouter API Integration Guide

## Общие принципы работы с OpenRouter

Все модели используют единый endpoint: `https://openrouter.ai/api/v1/chat/completions`

### Базовый формат запроса:

```typescript
const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
    'HTTP-Referer': window.location.href,
    'X-Title': 'AI Developer Agent',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'openai/gpt-5.2-chat', // ID модели из списка
    messages: [
      {
        role: 'system',
        content: 'You are an expert software developer assistant.'
      },
      {
        role: 'user',
        content: 'Create a React component for user authentication.'
      }
    ],
    temperature: 0.7,
    max_tokens: 4000
  })
});
```

## Специфика моделей по категориям

### 1. GPT-5.x серия (OpenAI)

**Модели:** `gpt-5.2-chat`, `gpt-5.2-pro`, `gpt-5.2`, `gpt-5.1`, `gpt-5.1-chat`, `gpt-5-pro`

**Оптимальные параметры:**
- `temperature`: 0.5-0.8 (для генерации кода)
- `top_p`: 0.9
- `max_tokens`: 2000-8000

**Особенности:**
- Лучше всего работают с четкими инструкциями
- Поддерживают function calling для структурированных выходов
- Рекомендуется использовать system prompt для задания контекста

**System prompt для кодинга:**
```
You are an expert software architect and developer. 
Generate clean, production-ready code following best practices.
Include error handling, type safety, and comprehensive comments.
```

### 2. Codex серия (Специализированные для кода)

**Модели:** `gpt-5.1-codex`, `gpt-5.1-codex-max`, `gpt-5-codex`

**Оптимальные параметры:**
- `temperature`: 0.2-0.5 (низкая для точности)
- `top_p`: 0.95
- `max_tokens`: 4000-16000

**Особенности:**
- Специально обучены на коде
- Лучше понимают технические спецификации
- Рекомендуется давать примеры входа/выхода

**System prompt:**
```
You are a specialized coding assistant. Generate syntactically correct, 
well-documented code. Focus on: type safety, error handling, performance, 
and following language-specific conventions.
```

### 3. O3 Deep Research

**Модель:** `openai/o3-deep-research`

**Оптимальные параметры:**
- `temperature`: 0.3-0.6
- `thinking_budget`: высокий (если доступно)
- `max_tokens`: 8000+

**Особенности:**
- Предназначена для глубокого анализа
- Медленнее, но качественнее для сложных задач
- Лучше использовать для архитектурных решений и рефакторинга

**System prompt:**
```
Analyze the codebase deeply. Consider: architecture patterns, performance bottlenecks,
security vulnerabilities, scalability issues, and best practices violations.
Provide detailed recommendations with examples.
```

### 4. Claude Opus/Sonnet (Anthropic)

**Модели:** `anthropic/claude-opus-4.5`, `anthropic/claude-sonnet-4.5`

**Оптимальные параметры:**
- `temperature`: 0.7 (Opus), 0.5 (Sonnet)
- `max_tokens`: 4000-8000
- Sonnet быстрее, Opus качественнее

**Особенности:**
- Отличное понимание контекста (до 200K токенов)
- Сильны в анализе и рефакторинге
- Хорошо работают с длинными файлами

**System prompt:**
```
You are Claude, an AI assistant specialized in software development.
Analyze code carefully, suggest improvements, and explain your reasoning.
Prioritize readability, maintainability, and security.
```

### 5. Grok Code (xAI)

**Модель:** `x-ai/grok-code-fast-1`

**Оптимальные параметры:**
- `temperature`: 0.6-0.8
- `max_tokens`: 2000-4000
- Оптимизирована для скорости

**Особенности:**
- Быстрая генерация
- Хороша для прототипирования
- Может быть менее детальной чем GPT

### 6. Qwen3 Coder

**Модели:** `qwen/qwen3-coder`, `qwen/qwen3-coder-plus`, `qwen/qwen3-coder:exacto`

**Оптимальные параметры:**
- `temperature`: 0.4-0.7
- `:exacto` вариант использует `temperature: 0.2` для точности

**Особенности:**
- Открытая модель, хорошая альтернатива
- Сильна в Python, JavaScript, TypeScript
- `:exacto` версия для строгого следования спецификациям

### 7. Mistral Codestral

**Модель:** `mistralai/codestral-2508`

**Оптимальные параметры:**
- `temperature`: 0.5-0.7
- `max_tokens`: 4000

**Особенности:**
- Европейская альтернатива
- Хороша для многоязычных проектов
- Поддержка fill-in-the-middle для автодополнений

### 8. Бесплатные модели

**Модели:** `kwaipilot/kat-coder-pro:free`, `qwen/qwen3-coder:free`

**Особенности:**
- Ограниченный контекст (16-20K токенов)
- Подходят для простых задач и экспериментов
- Могут иметь rate limits

## Рекомендации по выбору модели

### Для создания новых проектов:
1. **GPT-5.2 Pro** - комплексные проекты
2. **Claude Opus 4.5** - если нужен большой контекст
3. **GPT-5-Codex** - фокус на качестве кода

### Для анализа существующего кода:
1. **O3 Deep Research** - глубокий анализ
2. **Claude Opus 4.5** - длинные файлы
3. **GPT-5.1-Codex-Max** - детальный разбор

### Для быстрых правок:
1. **Grok Code Fast** - скорость
2. **Claude Sonnet 4.5** - баланс скорости и качества
3. **Qwen3 Coder Plus** - альтернатива

### Для рефакторинга:
1. **GPT-5-Codex** - структурные изменения
2. **Claude Opus 4.5** - сложный рефакторинг
3. **Qwen3 Coder Exacto** - точное следование правилам

## Обработка ошибок

```typescript
try {
  const response = await fetch(url, options);
  
  if (response.status === 429) {
    // Rate limit - подождать и повторить
    await sleep(1000);
    return retry();
  }
  
  if (response.status === 402) {
    // Недостаточно кредитов
    throw new Error('Insufficient credits');
  }
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  const data = await response.json();
  return data.choices[0].message.content;
  
} catch (error) {
  console.error('OpenRouter API error:', error);
  throw error;
}
```

## Streaming responses

Для больших ответов рекомендуется использовать streaming:

```typescript
const response = await fetch(url, {
  ...options,
  body: JSON.stringify({
    ...body,
    stream: true
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      if (data.choices[0].delta.content) {
        // Обработать чанк текста
        onChunk(data.choices[0].delta.content);
      }
    }
  }
}
```
