import { useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

interface AgentLog {
  agent: string;
  action: string;
  message: string;
  status: string;
  timestamp: string | null;
}

interface AgentConsoleProps {
  logs: AgentLog[];
  isActive: boolean;
}

const AGENT_LABELS: Record<string, { label: string; color: string }> = {
  architect: { label: 'Архитектор', color: 'text-purple-500' },
  frontend: { label: 'Frontend', color: 'text-blue-500' },
  backend: { label: 'Backend', color: 'text-green-500' },
  db: { label: 'БД', color: 'text-orange-500' },
  validator: { label: 'Валидатор', color: 'text-yellow-500' },
  deployer: { label: 'Деплой', color: 'text-red-500' },
};

const AgentConsole = ({ logs, isActive }: AgentConsoleProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Icon name="Terminal" size={16} />
          Консоль агентов
          {isActive && (
            <Badge variant="default" className="text-xs animate-pulse">LIVE</Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div
          ref={scrollRef}
          className="bg-muted/50 rounded-lg p-3 max-h-64 overflow-y-auto space-y-2 font-mono text-xs"
        >
          {logs.length === 0 && (
            <div className="text-muted-foreground text-center py-4">
              Ожидание запуска...
            </div>
          )}
          {logs.map((log, index) => {
            const agentInfo = AGENT_LABELS[log.agent] || { label: log.agent, color: 'text-foreground' };
            return (
              <div key={index} className="flex items-start gap-2">
                <span className="text-muted-foreground flex-shrink-0 w-14">
                  {log.timestamp ? new Date(log.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--:--'}
                </span>
                {log.status === 'success' ? (
                  <Icon name="Check" size={12} className="text-green-500 mt-0.5 flex-shrink-0" />
                ) : log.status === 'error' ? (
                  <Icon name="X" size={12} className="text-red-500 mt-0.5 flex-shrink-0" />
                ) : (
                  <Icon name="Loader2" size={12} className="text-primary animate-spin mt-0.5 flex-shrink-0" />
                )}
                <span className={`font-semibold flex-shrink-0 ${agentInfo.color}`}>
                  [{agentInfo.label}]
                </span>
                <span className="text-foreground break-all">{log.message}</span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default AgentConsole;
