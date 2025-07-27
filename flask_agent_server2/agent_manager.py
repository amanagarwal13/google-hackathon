"""
Agent Manager for ADK Agent Integration
Handles loading and executing ADK agents with proper error handling
"""

import os
import sys
import json
import asyncio
import threading
import queue
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import importlib.util
import traceback

# Configure logging
logger = logging.getLogger(__name__)


class AgentManager:
    """
    Manages ADK agent loading and execution
    Supports multiple agent types and execution patterns
    """
    
    def __init__(self, agent_path: str = None):
        self.agent = None
        self.agent_type = None
        self.agent_info = {}
        self.execution_queue = queue.Queue()
        self.agent_path = agent_path or os.environ.get('AGENT_PATH', './agents/oracle_agent')
        
        # Load the agent
        self._load_agent()
        
        # Start execution thread if needed
        if self.agent_type == 'async':
            self._start_async_executor()
    
    def _load_agent(self):
        """Load the ADK agent from the specified path"""
        try:
            # Normalize agent path
            agent_path = os.path.abspath(self.agent_path)
            agent_dir = os.path.dirname(agent_path)
            agent_package_name = os.path.basename(agent_path)
            
            # Add parent directory to Python path for package imports
            if agent_dir not in sys.path:
                sys.path.insert(0, agent_dir)
            
            agent_loaded = False
            
            # Pattern 1: Import as package (for agents with relative imports like Oracle Agent)
            try:
                logger.info(f"Attempting to load agent package: {agent_package_name}")
                
                # Import the package
                agent_package = importlib.import_module(agent_package_name)
                
                # Try to import the agent module within the package
                agent_module = importlib.import_module(f"{agent_package_name}.agent")
                
                # Look for common agent patterns
                if hasattr(agent_module, 'root_agent'):
                    self.agent = agent_module.root_agent
                    agent_loaded = True
                    logger.info(f"Found 'root_agent' in {agent_package_name}.agent")
                elif hasattr(agent_module, 'agent'):
                    self.agent = agent_module.agent
                    agent_loaded = True
                    logger.info(f"Found 'agent' in {agent_package_name}.agent")
                elif hasattr(agent_module, 'main_agent'):
                    self.agent = agent_module.main_agent
                    agent_loaded = True
                    logger.info(f"Found 'main_agent' in {agent_package_name}.agent")
                
                # Check package-level exports if agent.py didn't have the agent
                if not agent_loaded:
                    if hasattr(agent_package, 'root_agent'):
                        self.agent = agent_package.root_agent
                        agent_loaded = True
                        logger.info(f"Found 'root_agent' in {agent_package_name}.__init__")
                    elif hasattr(agent_package, 'agent'):
                        self.agent = agent_package.agent
                        agent_loaded = True
                        logger.info(f"Found 'agent' in {agent_package_name}.__init__")
                
                if agent_loaded:
                    self._detect_agent_type()
                    
            except Exception as e:
                logger.warning(f"Failed to load agent as package: {e}")
            
            # Pattern 2: Direct file import (fallback for simple agents without relative imports)
            if not agent_loaded:
                try:
                    logger.info("Attempting direct file import as fallback")
                    agent_module_path = os.path.join(agent_path, 'agent.py')
                    
                    if os.path.exists(agent_module_path):
                        spec = importlib.util.spec_from_file_location("agent_module", agent_module_path)
                        agent_module = importlib.util.module_from_spec(spec)
                        
                        # Set the module's __package__ to enable relative imports
                        agent_module.__package__ = agent_package_name
                        
                        spec.loader.exec_module(agent_module)
                        
                        # Look for common agent patterns
                        if hasattr(agent_module, 'root_agent'):
                            self.agent = agent_module.root_agent
                            agent_loaded = True
                        elif hasattr(agent_module, 'agent'):
                            self.agent = agent_module.agent
                            agent_loaded = True
                        elif hasattr(agent_module, 'main_agent'):
                            self.agent = agent_module.main_agent
                            agent_loaded = True
                        
                        if agent_loaded:
                            self._detect_agent_type()
                        
                except Exception as e:
                    logger.warning(f"Failed to load agent from direct file import: {e}")
            
            if agent_loaded:
                logger.info(f"✅ Successfully loaded agent from {self.agent_path}")
                self._extract_agent_info()
            else:
                raise Exception(f"Could not load agent from {self.agent_path}. Check agent structure and exports.")
                
        except Exception as e:
            logger.error(f"❌ Failed to load agent: {e}")
            logger.error(traceback.format_exc())
            self.agent = None
            self.agent_info = {
                'error': str(e),
                'loaded': False
            }
    
    def _detect_agent_type(self):
        """Detect the type of agent and its execution pattern"""
        if self.agent is None:
            return
        
        # Check for different agent patterns
        if hasattr(self.agent, 'run'):
            self.agent_type = 'sync_run'
        elif hasattr(self.agent, 'execute'):
            self.agent_type = 'sync_execute'
        elif hasattr(self.agent, 'arun') or hasattr(self.agent, 'async_run'):
            self.agent_type = 'async'
        elif hasattr(self.agent, '__call__'):
            self.agent_type = 'callable'
        else:
            # For ADK LlmAgent or Agent
            if hasattr(self.agent, 'process_query') or hasattr(self.agent, 'invoke'):
                self.agent_type = 'adk_agent'
            else:
                self.agent_type = 'unknown'
        
        logger.info(f"Detected agent type: {self.agent_type}")
    
    def _extract_agent_info(self):
        """Extract information about the loaded agent"""
        if self.agent is None:
            return
        
        self.agent_info = {
            'loaded': True,
            'type': self.agent_type,
            'name': getattr(self.agent, 'name', 'Unknown Agent'),
            'description': getattr(self.agent, 'description', ''),
            'model': getattr(self.agent, 'model', 'Unknown'),
            'capabilities': []
        }
        
        # Extract tools/capabilities
        if hasattr(self.agent, 'tools'):
            tools = getattr(self.agent, 'tools', [])
            for tool in tools:
                if hasattr(tool, 'name'):
                    self.agent_info['capabilities'].append({
                        'name': tool.name,
                        'description': getattr(tool, 'description', '')
                    })
        
        # Extract sub-agents if any
        if hasattr(self.agent, 'sub_agents'):
            self.agent_info['sub_agents'] = [
                {
                    'name': getattr(sa, 'name', 'Unknown'),
                    'description': getattr(sa, 'description', '')
                }
                for sa in getattr(self.agent, 'sub_agents', [])
            ]
    
    def is_agent_loaded(self) -> bool:
        """Check if agent is successfully loaded"""
        return self.agent is not None
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the loaded agent"""
        return self.agent_info
    
    def process_message(self, message: str, session_id: str, session_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a message with the loaded agent
        Returns response and metadata
        """
        if not self.is_agent_loaded():
            return {
                'response': "I'm sorry, but the agent is not properly loaded. Please check the server logs.",
                'metadata': {'error': True, 'agent_loaded': False}
            }
        
        try:
            # Prepare context
            context = self._prepare_context(message, session_id, session_data)
            
            # Execute based on agent type
            if self.agent_type == 'sync_run':
                response = self._execute_sync_run(message, context)
            elif self.agent_type == 'sync_execute':
                response = self._execute_sync_execute(message, context)
            elif self.agent_type == 'async':
                response = self._execute_async(message, context)
            elif self.agent_type == 'callable':
                response = self._execute_callable(message, context)
            elif self.agent_type == 'adk_agent':
                response = self._execute_adk_agent(message, context)
            else:
                response = self._execute_generic(message, context)
            
            return {
                'response': response,
                'metadata': {
                    'agent_type': self.agent_type,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            logger.error(traceback.format_exc())
            return {
                'response': f"I encountered an error while processing your request: {str(e)}",
                'metadata': {'error': True, 'error_message': str(e)}
            }
    
    def _prepare_context(self, message: str, session_id: str, session_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prepare context for agent execution"""
        context = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'message': message
        }
        
        if session_data:
            context['history'] = session_data.get('messages', [])
            context['session_context'] = session_data.get('context', {})
            context['agent_state'] = session_data.get('agent_state')
        
        return context
    
    def _execute_sync_run(self, message: str, context: Dict[str, Any]) -> str:
        """Execute agent with run() method"""
        try:
            result = self.agent.run(message)
            if isinstance(result, dict):
                return result.get('response', str(result))
            return str(result)
        except Exception as e:
            logger.error(f"Error in sync_run execution: {e}")
            raise
    
    def _execute_sync_execute(self, message: str, context: Dict[str, Any]) -> str:
        """Execute agent with execute() method"""
        try:
            result = self.agent.execute({
                'input': message,
                'context': context
            })
            if isinstance(result, dict):
                return result.get('output', result.get('response', str(result)))
            return str(result)
        except Exception as e:
            logger.error(f"Error in sync_execute execution: {e}")
            raise
    
    def _execute_async(self, message: str, context: Dict[str, Any]) -> str:
        """Execute async agent"""
        try:
            # Create a new event loop for this execution
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if hasattr(self.agent, 'arun'):
                result = loop.run_until_complete(self.agent.arun(message))
            elif hasattr(self.agent, 'async_run'):
                result = loop.run_until_complete(self.agent.async_run(message))
            else:
                raise Exception("No async method found")
            
            loop.close()
            
            if isinstance(result, dict):
                return result.get('response', str(result))
            return str(result)
        except Exception as e:
            logger.error(f"Error in async execution: {e}")
            raise
    
    def _execute_callable(self, message: str, context: Dict[str, Any]) -> str:
        """Execute callable agent"""
        try:
            result = self.agent(message)
            if isinstance(result, dict):
                return result.get('response', str(result))
            return str(result)
        except Exception as e:
            logger.error(f"Error in callable execution: {e}")
            raise
    
    def _execute_adk_agent(self, message: str, context: Dict[str, Any]) -> str:
        """Execute ADK-style agent"""
        try:
            # For ADK agents, we need to create a proper execution context
            # This is a simplified version - you may need to adjust based on your specific agent
            
            # Option 1: If agent has process_query method
            if hasattr(self.agent, 'process_query'):
                result = self.agent.process_query(
                    query=message,
                    session_id=context['session_id']
                )
                if isinstance(result, dict):
                    return result.get('response', result.get('output', str(result)))
                return str(result)
            
            # Option 2: If agent has invoke method (common in ADK)
            elif hasattr(self.agent, 'invoke'):
                result = self.agent.invoke({
                    'input': message,
                    'session_id': context['session_id'],
                    'history': context.get('history', [])
                })
                if isinstance(result, dict):
                    return result.get('output', result.get('response', str(result)))
                return str(result)
            
            # Option 3: Direct execution attempt
            else:
                # This is a fallback - ADK agents might need specific execution context
                # You may need to implement a proper ADK execution environment
                return "ADK agent execution not fully implemented. Please check the agent integration."
                
        except Exception as e:
            logger.error(f"Error in ADK agent execution: {e}")
            raise
    
    def _execute_generic(self, message: str, context: Dict[str, Any]) -> str:
        """Generic execution fallback"""
        try:
            # Try to find any method that might process the message
            possible_methods = ['process', 'handle', 'respond', 'chat']
            
            for method_name in possible_methods:
                if hasattr(self.agent, method_name):
                    method = getattr(self.agent, method_name)
                    if callable(method):
                        result = method(message)
                        if isinstance(result, dict):
                            return result.get('response', str(result))
                        return str(result)
            
            return "I'm not sure how to process your request with this agent type."
            
        except Exception as e:
            logger.error(f"Error in generic execution: {e}")
            raise
    
    def _start_async_executor(self):
        """Start a background thread for async execution if needed"""
        # This is for agents that require a persistent event loop
        # Implement if your agent needs this pattern
        pass


# Create a wrapper specifically for ADK agents
class ADKAgentWrapper:
    """
    Wrapper to make ADK agents compatible with the Flask interface
    """
    
    def __init__(self, adk_agent):
        self.agent = adk_agent
        self.name = getattr(adk_agent, 'name', 'ADK Agent')
        self.description = getattr(adk_agent, 'description', '')
        self.model = getattr(adk_agent, 'model', 'Unknown')
    
    def run(self, message: str) -> Dict[str, Any]:
        """
        Run the ADK agent with a message
        This method adapts the ADK agent interface to our expected format
        """
        try:
            # Create a minimal execution context for ADK
            context = {
                'input': message,
                'timestamp': datetime.now().isoformat()
            }
            
            # Try different execution patterns
            if hasattr(self.agent, 'invoke'):
                result = self.agent.invoke(context)
            elif hasattr(self.agent, 'run'):
                result = self.agent.run(message)
            elif hasattr(self.agent, '__call__'):
                result = self.agent(message)
            else:
                # For LlmAgent or similar
                # This is a simplified execution - you may need to implement
                # proper ADK execution context based on your specific needs
                result = {'response': 'ADK agent execution needs implementation'}
            
            # Normalize response
            if isinstance(result, str):
                return {'response': result}
            elif isinstance(result, dict):
                if 'output' in result:
                    return {'response': result['output']}
                elif 'response' in result:
                    return {'response': result['response']}
                else:
                    return {'response': str(result)}
            else:
                return {'response': str(result)}
                
        except Exception as e:
            logger.error(f"Error in ADK wrapper: {e}")
            return {'response': f'Error: {str(e)}'} 