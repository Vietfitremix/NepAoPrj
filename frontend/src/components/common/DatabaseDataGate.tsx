import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { api, errorMessage } from '../../services/api';
import { setWardrobeCatalogs } from '../../utils/maleWardrobe';
import type { WardrobeCatalog, WardrobeCharacter } from '../../utils/maleWardrobe';
import { setWardrobeStyles } from '../../utils/wardrobeStyles';
import { setStylistQuiz } from '../../utils/stylistQuiz';
import type { QuizQuestion } from '../../utils/stylistQuiz';
import { ErrorBox, Loading } from './UI';

interface BootstrapData {
  wardrobes:Record<WardrobeCharacter,WardrobeCatalog>;
  patterns:Parameters<typeof setWardrobeStyles>[0];
  colors:Parameters<typeof setWardrobeStyles>[1];
  quiz:QuizQuestion[]; assetCount:number;
}

export default function DatabaseDataGate({children}:{children:ReactNode}) {
  const [ready,setReady]=useState(false);
  const [error,setError]=useState('');
  const [retry,setRetry]=useState(0);
  useEffect(()=>{
    const controller=new AbortController();setError('');
    api.get<BootstrapData>('/data/bootstrap',{signal:controller.signal}).then(({data})=>{
      if(controller.signal.aborted)return;
      if(!data.assetCount)throw new Error('Tủ đồ trên máy chủ chưa được nhập đầy đủ.');
      setWardrobeCatalogs(data.wardrobes);setWardrobeStyles(data.patterns,data.colors);setStylistQuiz(data.quiz);
      setReady(true);
    }).catch(err=>{if(!controller.signal.aborted)setError(errorMessage(err));});
    return()=>controller.abort();
  },[retry]);
  if(!ready)return <main className="page-container nepao-page">
    {error?<ErrorBox message={error} retry={()=>setRetry(value=>value+1)}/>:<Loading text="Đang tải tủ đồ và dữ liệu từ máy chủ…"/>}
  </main>;
  return children;
}
