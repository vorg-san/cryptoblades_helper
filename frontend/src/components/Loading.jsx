import React from 'react'
import {usePromiseTracker} from 'react-promise-tracker'
import Loader from 'react-loader-spinner'

const Loading = () => {
  const {promiseInProgress} = usePromiseTracker()
  return (
    promiseInProgress && (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          opacity: 0.5,
          background: '#000',
          zIndex: 10,
          top: 0,
          left: 0,
          position: 'fixed',
        }}
      >
        <Loader type='ThreeDots' color='#2BAD60' height='100' width='100' />
      </div>
    )
  )
}

export default Loading
