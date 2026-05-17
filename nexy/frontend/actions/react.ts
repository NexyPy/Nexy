import { useState } from 'react';
import { transport } from './nexy-client';

type ActionState = {
  loading: boolean;
  data: unknown | null;
  error: unknown | null;
};
export function useAction(actionPath: string) {
  const [state, setState] = useState<ActionState>({ loading: false, data: null, error: null });

  const execute = async (args: unknown | unknown) => {
    setState({ loading: true, data: null, error: null });
    try {
      const data = await transport.call(actionPath, args);
      setState({ loading: false, data, error: null });
      return data;
    } catch (e) {
      setState({ loading: false, data: null, error: e });
    }
  };

  return [execute, state];
}