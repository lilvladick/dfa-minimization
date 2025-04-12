export function checkDeterminism(transitions) {
    // Для каждого состояния (источника) создаём объект, где ключ – символ, а значение – число переходов с этим символом.
    const transitionCount = {};
  
    for (let t of transitions) {
      if (!transitionCount[t.from]) {
        transitionCount[t.from] = {};
      }
      // увеличиваеть счетчик если символ был
      transitionCount[t.from][t.symbol] = (transitionCount[t.from][t.symbol] || 0) + 1;
      // НКА если переход больше чем 1 по одному символу
      if (transitionCount[t.from][t.symbol] > 1) {
        return false;
      }
    }
  
    return true;
  }