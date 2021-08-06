import axios from 'axios'
import {trackPromise} from 'react-promise-tracker'

const raizMy = 'http://localhost:8000/'
const urlsMy = {
  weapons: {
    metodo: 'g',
    url: 'api/weapons',
    dados: {},
  },
  loadWeapons: {
    metodo: 'g',
    url: 'market/load_weapons',
    dados: {},
  },
}
const axiosMy = axios.create({
  baseURL: raizMy,
})

export const apiMyE = async (...args) => {
  return trackPromise(api(axiosMy, urlsMy, ...args))
}

export const apiMy = async (...args) => {
  let [res, err] = await trackPromise(api(axiosMy, urlsMy, ...args))

  if (err) {
    alert('Erro na chamada API: ' + args[0])
  } else {
    return res
  }
}

const raizCB = 'http://localhost:8000/api/'
const urlsCB = {
}
const axiosCB = axios.create({
  baseURL: raizCB,
})

export const apiCBE = async (...args) => {
  return trackPromise(api(axiosCB, urlsCB, ...args))
}

export const apiCB = async (...args) => {
  let [res, err] = await trackPromise(api(axiosCB, urlsCB, ...args))

  if (err) {
    alert('Erro na chamada API: ' + args[0])
  } else {
    return res
  }
}

// -------------------------

async function api(axi, urls, url, dados) {
  if (urls[url].resposta) return [urls[url].resposta, null]

  let res = null
  let err = null

  try {
    if (!dados) dados = urls[url].dados

    let u = urls[url].url

    const regex = RegExp(':\\w+', 'g')
    let r
    while ((r = regex.exec(u)) !== null) {
      if (dados[r[0].substring(1)]) {
        u = u.replace(r[0], dados[r[0].substring(1)])
        delete dados[r[0].substring(1)]
        regex.lastIndex = 1
      }
    }

    if (urls[url].metodo === 'p') {
      res = await axi.post(u, dados)
    } else {
      res = await axi.get(u)
    }

    res = res.data
  } catch (e) {
    err = e
    console.log('erro na api:', e, e?.status)
  }

  return [res, err]
}
