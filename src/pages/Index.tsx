import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';
import { AI_MODELS } from '@/config/ai-models';
import CreateProjectForm from '@/components/CreateProjectForm';
import SettingsDialog from '@/components/SettingsDialog';
import AgentArchitectureFlow from '@/components/AgentArchitectureFlow';
import PlatformComparison from '@/components/PlatformComparison';
import ExampleWorkflow from '@/components/ExampleWorkflow';

const Index = () => {
  const [activeTab, setActiveTab] = useState('create');
  const [language, setLanguage] = useState('ru');
  const [aiModel, setAiModel] = useState(AI_MODELS[0].id);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const handleGitHubConnect = async () => {
    setIsConnecting(true);
    try {
      const githubUrl = `https://github.com/login/oauth/authorize?client_id=Ov23liCl4I7JbP2Bt2Ob&scope=repo,workflow`;
      window.location.href = githubUrl;
    } catch (error) {
      console.error('GitHub connection error:', error);
    } finally {
      setIsConnecting(false);
    }
  };

  const tabs = [
    { id: 'create', label: 'Создание', icon: 'Plus' },
    { id: 'architecture', label: 'Архитектура', icon: 'Layers' },
    { id: 'comparison', label: 'Сравнение', icon: 'BarChart3' },
    { id: 'workflow', label: 'Демо', icon: 'Play' },
    { id: 'github', label: 'GitHub', icon: 'Github' },
    { id: 'docs', label: 'Документация', icon: 'FileText' },
  ];

  const selectedModel = AI_MODELS.find(m => m.id === aiModel) || AI_MODELS[0];

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border/40 bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <Icon name="Sparkles" className="text-white" size={20} />
              </div>
              <div>
                <h1 className="text-xl font-semibold">AI Developer Agent</h1>
                <p className="text-xs text-muted-foreground">Интеллектуальный помощник программиста</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="px-3 py-2 rounded-lg border border-input bg-background text-sm"
              >
                <option value="ru">🇷🇺 Русский</option>
                <option value="en">🇬🇧 English</option>
                <option value="zh">🇨🇳 中文</option>
                <option value="es">🇪🇸 Español</option>
              </select>

              <select
                value={aiModel}
                onChange={(e) => setAiModel(e.target.value)}
                className="px-3 py-2 rounded-lg border border-input bg-background text-sm min-w-[200px]"
              >
                <optgroup label="Pro модели">
                  {AI_MODELS.filter(m => m.category === 'pro').map(model => (
                    <option key={model.id} value={model.id}>{model.name}</option>
                  ))}
                </optgroup>
                <optgroup label="Стандартные">
                  {AI_MODELS.filter(m => m.category === 'standard').map(model => (
                    <option key={model.id} value={model.id}>{model.name}</option>
                  ))}
                </optgroup>
                <optgroup label="Специализированные">
                  {AI_MODELS.filter(m => m.category === 'specialized').map(model => (
                    <option key={model.id} value={model.id}>{model.name}</option>
                  ))}
                </optgroup>
                <optgroup label="Бесплатные">
                  {AI_MODELS.filter(m => m.category === 'free').map(model => (
                    <option key={model.id} value={model.id}>{model.name}</option>
                  ))}
                </optgroup>
              </select>

              <Button variant="outline" size="icon" onClick={() => setSettingsOpen(true)}>
                <Icon name="Settings" size={18} />
              </Button>
            </div>
          </div>
          
          {selectedModel && (
            <div className="mt-3 p-2 bg-muted rounded-lg text-xs">
              <span className="font-medium">{selectedModel.provider}</span> • {selectedModel.description}
              {selectedModel.specialties && (
                <span className="ml-2 text-muted-foreground">
                  • {selectedModel.specialties.join(', ')}
                </span>
              )}
            </div>
          )}
        </div>
      </header>

      <SettingsDialog open={settingsOpen} onOpenChange={setSettingsOpen} />

      <main className="container mx-auto px-4 py-8">
        <div className="animate-scale-in">
          <div className="flex flex-wrap gap-2 mb-8 border-b border-border">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary text-primary font-medium'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              >
                <Icon name={tab.icon} size={16} />
                {tab.label}
              </button>
            ))}
          </div>

          <div className="animate-fade-in">
            {activeTab === 'create' && (
              <CreateProjectForm aiModel={aiModel} language={language} />
            )}

            {activeTab === 'architecture' && (
              <AgentArchitectureFlow />
            )}

            {activeTab === 'comparison' && (
              <PlatformComparison />
            )}

            {activeTab === 'workflow' && (
              <ExampleWorkflow />
            )}

            {activeTab === 'github' && (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center py-12">
                    <Icon name="Github" size={48} className="mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-xl font-semibold mb-2">GitHub Интеграция</h3>
                    <p className="text-muted-foreground mb-6">
                      Подключите GitHub для автоматической синхронизации кода
                    </p>
                    <Button size="lg" onClick={handleGitHubConnect} disabled={isConnecting}>
                      <Icon name="Link" className="mr-2" size={18} />
                      {isConnecting ? 'Подключение...' : 'Подключить GitHub'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {activeTab === 'docs' && (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center py-12">
                    <Icon name="FileText" size={48} className="mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-xl font-semibold mb-2">Автоматическая документация</h3>
                    <p className="text-muted-foreground mb-6">
                      Агент генерирует и поддерживает документацию в актуальном состоянии
                    </p>
                    <Button size="lg">
                      <Icon name="Sparkles" className="mr-2" size={18} />
                      Сгенерировать документацию
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>

      <footer className="border-t border-border/40 mt-16">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-muted-foreground flex-wrap gap-4">
            <p>© 2026 AI Developer Agent. Автоматизация разработки ПО.</p>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="gap-1 flex items-center">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                Система активна
              </Badge>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;