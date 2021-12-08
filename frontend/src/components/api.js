import axios from 'axios'
import {trackPromise} from 'react-promise-tracker'

const raizMy = 'http://localhost:7000/'
const urlsMy = {
  weapons: {
    metodo: 'g',
    url: 'api/weapons',
    dados: {},
  },
  characters: {
    metodo: 'g',
    url: 'api/characters',
    dados: {},
  },
  personal_account: {
    metodo: 'g',
    url: 'api/personal_account',
    dados: {},
  },
  transfer_character: {
    metodo: 'p',
    url: 'market/transfer_character',
    dados: {from: null, to: null, charId: null},
  },
  transfer_weapon: {
    metodo: 'p',
    url: 'market/transfer_weapon',
    dados: {from: null, to: null, weaponId: null},
  },
  do_fights: {
    metodo: 'p',
    url: 'market/do_fights',
    dados: {max_num_figths : 0},
  },
	load_weapons: {
    metodo: 'g',
    url: 'market/load_weapons',
    dados: {},
  },
	clean_weapons: {
    metodo: 'g',
    url: 'market/clean_weapons',
    dados: {},
  },
	clean_chars: {
    metodo: 'g',
    url: 'market/clean_chars',
    dados: {},
  },
  read_market_weapons: {
    metodo: 'g',
    url: 'market/read_market_weapons',
    dados: {},
  },
  read_market_chars: {
    metodo: 'g',
    url: 'market/read_market_chars',
    dados: {},
  },
  from_game_to_stake: {
    metodo: 'g',
    url: 'market/from_game_to_stake',
    dados: {},
  },
  update_items_account: {
    metodo: 'p',
    url: 'market/update_items_account',
    dados: {accounts: null},
  },
  update_experience_table: {
    metodo: 'g',
    url: 'market/update_experience_table',
    dados: {},
  },
  experience_table: {
    metodo: 'g',
    url: 'api/xp_table',
    dados: {},
  },
  price: {
    metodo: 'g',
    url: 'api/price',
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
