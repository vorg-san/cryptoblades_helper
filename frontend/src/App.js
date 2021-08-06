import './App.css'
import React, {useState, useEffect, useCallback} from 'react'
import {apiMy} from './components/api'
import Loading from './components/Loading'

function App() {
	const [weapons, setWeapons] = useState([{weaponId:23424, price:0.5}]);

	const loadDB = useCallback(async () => {
		setWeapons(await apiMy('weapons'))
	}, [])

	useEffect(() => {
		loadDB()
	}, [loadDB]);

	async function readWeapons() {
		await apiMy('loadWeapons')
		loadDB()
	}

  return (
		<>
		<main className="content">
			<div className="row">
				<button type='button' className="btn btn-primary" onClick={readWeapons}>
					Load from CB market
				</button>
				<div className="card p-3">
					<ul className="list-group list-group-flush">
					{weapons.map(w => (
					<div>
						<h1>{w.weaponId}</h1>
						<span>{w.price}</span>
					</div>
					))}
					</ul>
				</div>
			</div>
		</main>
		<Loading />
		</>
  )
}

export default App
