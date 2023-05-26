const BtnDelete = document.querySelectorAll('btn-delete')

if(BtnDelete)
{
  const Array = Array.from(BtnDelete);
  Array.array.forEach(btn => {
    btn.addEventListener('click', (e) => {
    if(!confirm('Seguro que quiere eliminar este registro?'))
    {
        e.preventDefault();
    }
    })

  });
}