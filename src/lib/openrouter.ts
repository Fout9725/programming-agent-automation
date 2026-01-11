export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface OpenRouterOptions {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  stream?: boolean;
}

export class OpenRouterClient {
  private apiKey: string;
  private baseUrl = 'https://openrouter.ai/api/v1/chat/completions';

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async chat(options: OpenRouterOptions): Promise<string> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'HTTP-Referer': window.location.href,
        'X-Title': 'AI Developer Agent',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: options.model,
        messages: options.messages,
        temperature: options.temperature ?? 0.7,
        max_tokens: options.max_tokens ?? 4000,
        top_p: options.top_p ?? 0.9,
        stream: options.stream ?? false
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`OpenRouter API error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();
    return data.choices[0].message.content;
  }

  async chatStream(
    options: OpenRouterOptions,
    onChunk: (text: string) => void
  ): Promise<void> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'HTTP-Referer': window.location.href,
        'X-Title': 'AI Developer Agent',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...options,
        stream: true
      })
    });

    if (!response.ok) {
      throw new Error(`OpenRouter API error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;

          try {
            const parsed = JSON.parse(data);
            const content = parsed.choices[0]?.delta?.content;
            if (content) onChunk(content);
          } catch (e) {
            console.error('Failed to parse stream chunk:', e);
          }
        }
      }
    }
  }

  getModelConfig(modelId: string): Partial<OpenRouterOptions> {
    if (modelId.includes('codex')) {
      return {
        temperature: 0.3,
        max_tokens: 8000,
        top_p: 0.95
      };
    }

    if (modelId.includes('claude')) {
      return {
        temperature: 0.7,
        max_tokens: 8000,
        top_p: 0.9
      };
    }

    if (modelId.includes('o3-deep-research')) {
      return {
        temperature: 0.4,
        max_tokens: 12000,
        top_p: 0.95
      };
    }

    if (modelId.includes('grok')) {
      return {
        temperature: 0.7,
        max_tokens: 4000,
        top_p: 0.9
      };
    }

    if (modelId.includes('qwen') && modelId.includes('exacto')) {
      return {
        temperature: 0.2,
        max_tokens: 6000,
        top_p: 0.95
      };
    }

    return {
      temperature: 0.7,
      max_tokens: 4000,
      top_p: 0.9
    };
  }

  getSystemPrompt(taskType: 'create' | 'analyze' | 'modify' | 'test' | 'docs'): string {
    const prompts = {
      create: `You are an expert software architect and developer. 
Generate clean, production-ready code following best practices.
Include error handling, type safety, and comprehensive comments.
Use modern frameworks and patterns appropriate for the project type.`,

      analyze: `You are a code analysis expert. Analyze code carefully for:
- Architecture patterns and design issues
- Performance bottlenecks
- Security vulnerabilities
- Code smells and anti-patterns
- Best practices violations
Provide specific, actionable recommendations with examples.`,

      modify: `You are a code refactoring specialist. When modifying code:
- Preserve existing functionality
- Improve code quality and readability
- Add proper error handling
- Follow the existing code style
- Document changes clearly`,

      test: `You are a test automation expert. Create comprehensive tests that:
- Cover all critical functionality
- Use appropriate testing frameworks
- Include unit, integration, and edge cases
- Follow testing best practices
- Are maintainable and readable`,

      docs: `You are a technical documentation specialist. Generate documentation that:
- Is clear and comprehensive
- Includes examples and use cases
- Follows standard documentation formats
- Is easy to navigate and search
- Stays synchronized with code changes`
    };

    return prompts[taskType];
  }
}

export function createOpenRouterClient(apiKey?: string): OpenRouterClient | null {
  const key = apiKey || localStorage.getItem('openrouter_api_key');
  if (!key) return null;
  return new OpenRouterClient(key);
}
