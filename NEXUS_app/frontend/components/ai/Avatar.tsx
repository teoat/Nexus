import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HelpCircle, MessageCircle, Sparkles, X, ChevronDown } from 'lucide-react';

interface AvatarProps {
  isVisible: boolean;
  context: UserContext;
  onInteraction: (action: string) => void;
}

interface UserContext {
  currentPage: string;
  userRole: string;
  workflowStep?: string;
  hasUnreadSuggestions?: boolean;
}

interface Suggestion {
  id: string;
  title: string;
  description: string;
  type: 'help' | 'tip' | 'action' | 'warning';
  priority: 'low' | 'medium' | 'high';
  action?: string;
}

const Avatar: React.FC<AvatarProps> = ({ isVisible, context, onInteraction }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Load contextual suggestions based on current context
    loadSuggestions(context);
  }, [context]);

  const loadSuggestions = async (userContext: UserContext) => {
    setIsLoading(true);
    try {
      // Simulate API call to get contextual suggestions
      const mockSuggestions: Suggestion[] = [
        {
          id: '1',
          title: 'Quick Start Guide',
          description: 'Get started with your first investigation',
          type: 'help',
          priority: 'high',
          action: 'open-quickstart'
        },
        {
          id: '2',
          title: 'Dashboard Tips',
          description: 'Optimize your dashboard layout',
          type: 'tip',
          priority: 'medium',
          action: 'optimize-dashboard'
        },
        {
          id: '3',
          title: 'Workflow Assistant',
          description: 'Need help with your current workflow?',
          type: 'action',
          priority: 'high',
          action: 'workflow-help'
        }
      ];

      setSuggestions(mockSuggestions);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: Suggestion) => {
    onInteraction(suggestion.action || suggestion.id);
    setIsExpanded(false);
  };

  const avatarVariants = {
    hidden: { scale: 0, opacity: 0 },
    visible: { scale: 1, opacity: 1 },
    hover: { scale: 1.1, transition: { duration: 0.2 } }
  };

  const panelVariants = {
    hidden: { 
      opacity: 0, 
      y: 20, 
      scale: 0.95,
      transition: { duration: 0.2 }
    },
    visible: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: { 
        duration: 0.3,
        ease: "easeOut"
      }
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed top-4 right-4 z-50">
      <motion.div
        variants={avatarVariants}
        initial="hidden"
        animate="visible"
        whileHover="hover"
        className="relative"
      >
        {/* Main Avatar Button */}
        <motion.button
          onClick={() => setIsExpanded(!isExpanded)}
          className={`
            w-14 h-14 rounded-full shadow-lg border-2 border-white
            bg-gradient-to-br from-blue-500 to-purple-600
            flex items-center justify-center text-white
            hover:shadow-xl transition-shadow duration-300
            ${context.hasUnreadSuggestions ? 'animate-pulse' : ''}
          `}
          whileTap={{ scale: 0.95 }}
        >
          <Sparkles className="w-6 h-6" />
          
          {/* Notification Badge */}
          {context.hasUnreadSuggestions && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center"
            >
              <span className="text-xs text-white font-bold">!</span>
            </motion.div>
          )}
        </motion.button>

        {/* Expanded Panel */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              variants={panelVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
              className="absolute top-16 right-0 w-80 bg-white rounded-lg shadow-2xl border border-gray-200 overflow-hidden"
            >
              {/* Panel Header */}
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Sparkles className="w-5 h-5" />
                    <h3 className="font-semibold">Frenly Assistant</h3>
                  </div>
                  <button
                    onClick={() => setIsExpanded(false)}
                    className="hover:bg-white/20 rounded-full p-1 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-sm text-blue-100 mt-1">
                  Your AI-powered guide to the Nexus Platform
                </p>
              </div>

              {/* Panel Content */}
              <div className="p-4 max-h-96 overflow-y-auto">
                {isLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {/* Contextual Info */}
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-sm text-gray-600">
                        <strong>Current Context:</strong> {context.currentPage}
                      </p>
                      <p className="text-sm text-gray-600">
                        <strong>Role:</strong> {context.userRole}
                      </p>
                    </div>

                    {/* Suggestions */}
                    <div className="space-y-2">
                      <h4 className="font-medium text-gray-900 flex items-center">
                        <HelpCircle className="w-4 h-4 mr-2" />
                        Suggested Actions
                      </h4>
                      
                      {suggestions.map((suggestion) => (
                        <motion.button
                          key={suggestion.id}
                          onClick={() => handleSuggestionClick(suggestion)}
                          className={`
                            w-full text-left p-3 rounded-lg border transition-colors
                            hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500
                            ${suggestion.priority === 'high' ? 'border-red-200 bg-red-50' : 
                              suggestion.priority === 'medium' ? 'border-yellow-200 bg-yellow-50' : 
                              'border-gray-200 bg-white'}
                          `}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <div className="flex items-start space-x-3">
                            <div className={`
                              w-2 h-2 rounded-full mt-2 flex-shrink-0
                              ${suggestion.type === 'help' ? 'bg-blue-500' :
                                suggestion.type === 'tip' ? 'bg-green-500' :
                                suggestion.type === 'action' ? 'bg-purple-500' :
                                'bg-red-500'}
                            `} />
                            <div className="flex-1">
                              <h5 className="font-medium text-gray-900 text-sm">
                                {suggestion.title}
                              </h5>
                              <p className="text-xs text-gray-600 mt-1">
                                {suggestion.description}
                              </p>
                            </div>
                          </div>
                        </motion.button>
                      ))}
                    </div>

                    {/* Quick Actions */}
                    <div className="border-t pt-3">
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                        <MessageCircle className="w-4 h-4 mr-2" />
                        Quick Actions
                      </h4>
                      <div className="grid grid-cols-2 gap-2">
                        <button
                          onClick={() => onInteraction('open-help')}
                          className="p-2 text-xs bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
                        >
                          Help Center
                        </button>
                        <button
                          onClick={() => onInteraction('open-tutorials')}
                          className="p-2 text-xs bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors"
                        >
                          Tutorials
                        </button>
                        <button
                          onClick={() => onInteraction('open-feedback')}
                          className="p-2 text-xs bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors"
                        >
                          Feedback
                        </button>
                        <button
                          onClick={() => onInteraction('open-settings')}
                          className="p-2 text-xs bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          Settings
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Panel Footer */}
              <div className="bg-gray-50 px-4 py-2 border-t">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Powered by Frenly AI</span>
                  <span>v1.0.0</span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default Avatar;
