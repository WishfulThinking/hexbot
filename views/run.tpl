% include('header.tpl')
<div id="container">
  <div class="offset-xl-2 col-xl-8">
    <a class="text-dark" href='/'><h1 class="display-3">HexBet</h1></a>
    <h1>Results for Run #{{run_id}}</h1>
    <table id="maintable" class="table table-striped">
      <thead class="thead-dark">
        <tr>
          <th scope="col">Run #</th>
          <th scope="col">Start Time (UTC)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th scope="row">4</th>
          <td><a href="/run/4">2018-01-25 22:22</a></td>
        </tr>
        <tr>
          <th scope="row">3</th>
          <td><a href="/run/3">2018-01-25 03:29</a></td>
        </tr>
        <tr>
          <th scope="row">2</th>
          <td><a href="/run/2">2018-01-25 02:56</a></td>
        </tr>
        <tr>
          <th scope="row">1</th>
          <td><a href="/run/1">2018-01-24 23:39</a></td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
% include('footer.tpl')