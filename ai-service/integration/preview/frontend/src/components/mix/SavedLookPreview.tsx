import { useEffect, useState } from 'react';
import type { MixConfig, Outfit } from '../../types';
import { getOutfit } from '../../services/outfitApi';
import { errorMessage } from '../../services/api';
import { ErrorBox, Loading } from '../common/UI';
import Avatar2D from './Avatar2D';
export default function SavedLookPreview({ config }: { config: MixConfig }) {
  const [outfit, setOutfit] = useState<Outfit>();
  const [error, setError] = useState('');
  useEffect(() => { const controller = new AbortController(); setOutfit(undefined); setError('');
    getOutfit(config.outfitCode, controller.signal).then(o => { if (!controller.signal.aborted) setOutfit(o); })
      .catch(e => { if (!controller.signal.aborted) setError(errorMessage(e)); });
    return () => controller.abort(); }, [config.outfitCode]);
  return error ? <ErrorBox message={error}/> : outfit ? <Avatar2D outfit={outfit} config={config}/> : <Loading text="Đang tải bản phối 2D…"/>;
}
