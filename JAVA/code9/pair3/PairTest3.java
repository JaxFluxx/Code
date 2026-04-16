package pair3;

/**
 * @version 1.01 2012-01-26
 * @author Cay Horstmann
 */
public class PairTest3
{
   public static void main(String[] args)
   {
      Manager ceo = new Manager("Gus Greedy", 800000, 1981, 12, 15);
      Manager cfo = new Manager("Sid Sneaky", 600000, 1980, 3, 4);
      Pair<Manager> buddies = new Pair<>(ceo, cfo);      
      printBuddies(buddies);
      
      Employee e1=new Employee("李伟",100000,1990,1,12);
      Employee e2=new Employee("赵晓峰",150000,1988,10,20);      
      Pair<Employee> partners =new Pair<>(e1,e2);
      printBuddies1(partners);
            

      ceo.setBonus(1000000);
      cfo.setBonus(500000);
      Manager[] managers = { ceo, cfo };

      Pair<Employee> result = new Pair<>();
      minmaxBonus(managers, result);
      System.out.println("first: " + result.getFirst().getName() 
         + ", second: " + result.getSecond().getName());
      maxminBonus(managers, result);
      System.out.println("first: " + result.getFirst().getName() 
         + ", second: " + result.getSecond().getName());
   }

   public static void printBuddies(Pair<? extends Employee> p)
   {
      Employee first = p.getFirst();
      Employee second = p.getSecond();

      System.out.println(first.getName() + " and " + second.getName() + " are buddies.");
//      p.setFirst(null);  // 只可以赋值为null
   }
   
   //作用等同的方法，可以使用传入对象的修改器
   public static <T extends Employee> void printBuddies1(Pair<T> p)
   {
	  Employee e=new Employee("调研员");
	  p.setSecond((T) e);
	  Employee first = p.getFirst();
      Employee second = p.getSecond();      
      System.out.println(first.getName() + " and " + second.getName() + " are buddies.");      
   }

   public static void minmaxBonus(Manager[] a, Pair<? super Manager> result)
   {
      if (a.length == 0) return;
      Manager min = a[0];
      Manager max = a[0];
      for (int i = 1; i < a.length; i++)
      {
         if (min.getBonus() > a[i].getBonus()) min = a[i];
         if (max.getBonus() < a[i].getBonus()) max = a[i];
      }
      result.setFirst(min);
      result.setSecond(max);
      Object e=result.getFirst();  //getFirst 的返回值为Object类型
   }

   public static void maxminBonus(Manager[] a, Pair<? super Manager> result)
   {
      minmaxBonus(a, result);
      PairAlg.swapHelper(result); // OK--swapHelper captures wildcard type
   }
   // Can't write public static <T super manager> ...
}

class PairAlg
{
   public static boolean hasNulls(Pair<?> p)
   {
      return p.getFirst() == null || p.getSecond() == null;
   }

   public static void swap(Pair<?> p) { swapHelper(p); }

   public static <T> void swapHelper(Pair<T> p)
   {
      T t = p.getFirst();
      p.setFirst(p.getSecond());
      p.setSecond(t);
   }

}


